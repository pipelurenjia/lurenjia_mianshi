#!/usr/bin/env python3
"""
Skill Snapshot - OpenCode Port
A tool for creating and managing snapshots of OpenCode skills.
Stores backups in a private GitHub repository.
"""

# Fix Windows encoding issues
import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Configuration
REPO_NAME = "skill-snapshots"
SKILL_DIR = Path.home() / ".config" / "opencode" / "skills"
LOCAL_REPO = Path.home() / ".opencode" / "skill-snapshots"

# Find gh executable - check common locations on Windows
def find_gh():
    if sys.platform == "win32":
        # Try common paths (use backslash for Windows)
        paths = [
            r"C:\Program Files\GitHub CLI\gh.exe",
            r"C:\Program Files (x86)\GitHub CLI\gh.exe",
        ]
        for p in paths:
            if Path(p).exists():
                return p
        # Try using where command
        result = subprocess.run('where gh', shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')[0]
    return "gh"

GH_CMD = find_gh()

# Skip rules configuration
SKIP_RULES = {
    "archive": "归档目录",
    "symlink": "符号链接（外部安装）",
    "self": "快照工具本身",
    "git": "自带 Git 版本控制",
    "dependencies": "包含依赖目录 (.venv/node_modules)",
    "too_large": "体积过大 (>10MB)",
    "no_skill_md": "缺少 SKILL.md",
}

def run_cmd(cmd, cwd=None, capture=True, shell=True):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            cwd=cwd,
            capture_output=capture,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def check_gh_available():
    """Check if GitHub CLI is available and authenticated."""
    code, stdout, _ = run_cmd(f'"{GH_CMD}" auth status')
    if code != 0:
        print("错误: GitHub CLI 未安装或未认证")
        print("请运行: gh auth login")
        return False
    return True


def get_github_user():
    """Get authenticated GitHub username."""
    code, stdout, _ = run_cmd(f'"{GH_CMD}" api user -q ".login"')
    if code != 0:
        return None
    return stdout.strip()


def ensure_skill_dir():
    """Ensure skills directory exists."""
    global SKILL_DIR
    
    # Check project-level skills first
    project_skill_dir = Path.cwd() / ".opencode" / "skills"
    if project_skill_dir.exists():
        SKILL_DIR = project_skill_dir
    
    if not SKILL_DIR.exists():
        print(f"错误: 技能目录不存在: {SKILL_DIR}")
        return False
    return True


# ============================================================================
# SCAN COMMAND
# ============================================================================

def scan_skills():
    """Scan skills directory and identify which need backup."""
    if not ensure_skill_dir():
        return
    
    backup_list = []
    skip_list = []
    
    print("=== 技能快照扫描 ===\n")
    
    for skill_path in sorted(SKILL_DIR.iterdir()):
        if not skill_path.is_dir():
            continue
        
        skill_name = skill_path.name
        result = check_skill(skill_path, skill_name)
        
        if result["should_skip"]:
            skip_list.append(result)
        else:
            backup_list.append(result)
    
    # Output skills needing backup
    print("【需要备份】")
    if not backup_list:
        print("  (无)")
    else:
        for item in backup_list:
            if item.get("has_snapshot"):
                print(f"  [x] {item['name']} ({item['info']}) [已有: {item['has_snapshot']}]")
            else:
                print(f"  [o] {item['name']} ({item['info']}) [未备份]")
    
    # Output skipped skills
    print("\n【跳过】")
    if not skip_list:
        print("  (无)")
    else:
        for item in skip_list:
            print(f"  [-] {item['name']} - {item['reason']}")
    
    # Statistics
    print("\n" + "=" * 40)
    print(f"需要备份: {len(backup_list)} 个")
    print(f"跳过: {len(skip_list)} 个")
    
    # Show skills needing backup
    needs_backup = [item["name"] for item in backup_list if not item.get("has_snapshot")]
    if needs_backup:
        print(f"\n【待备份】{len(needs_backup)} 个技能尚未创建快照:")
        for name in needs_backup:
            print(f"  - {name}")


def check_skill(skill_path, skill_name):
    """Check a single skill against skip rules."""
    result = {
        "path": skill_path,
        "name": skill_name,
        "should_skip": False,
        "reason": None,
        "info": None,
        "has_snapshot": None,
    }
    
    # Rule 1: archive directory
    if skill_name == "archive":
        result["should_skip"] = True
        result["reason"] = SKIP_RULES["archive"]
        return result
    
    # Rule 2: symlink (external install)
    if skill_path.is_symlink():
        result["should_skip"] = True
        result["reason"] = SKIP_RULES["symlink"]
        return result
    
    # Rule 3: snapshot tool itself
    if skill_name == "skill-snapshot":
        result["should_skip"] = True
        result["reason"] = SKIP_RULES["self"]
        return result
    
    # Rule 4: contains .git (version controlled)
    if (skill_path / ".git").exists():
        result["should_skip"] = True
        result["reason"] = SKIP_RULES["git"]
        return result
    
    # Rule 5: contains .venv or node_modules
    if (skill_path / ".venv").exists() or (skill_path / "node_modules").exists():
        result["should_skip"] = True
        result["reason"] = SKIP_RULES["dependencies"]
        return result
    
    # Rule 6: size > 10MB
    size_kb = get_dir_size(skill_path)
    if size_kb > 10240:
        size_mb = size_kb / 1024
        result["should_skip"] = True
        result["reason"] = SKIP_RULES["too_large"].format(size_mb)
        return result
    
    # Rule 7: no SKILL.md
    if not (skill_path / "SKILL.md").exists():
        result["should_skip"] = True
        result["reason"] = SKIP_RULES["no_skill_md"]
        return result
    
    # Calculate file count and size
    files = sum(1 for f in skill_path.rglob("*") if f.is_file() and f.name != ".DS_Store")
    size = get_dir_size(skill_path) / 1024  # KB to MB
    result["info"] = f"{files} files, {size:.1f}M"
    
    # Check if already has snapshot
    if LOCAL_REPO.exists() and (LOCAL_REPO / ".git").exists():
        result["has_snapshot"] = get_latest_snapshot(skill_name)
    
    return result


def get_dir_size(path):
    """Get directory size in KB."""
    total = 0
    for entry in path.rglob("*"):
        if entry.is_file() and entry.name != ".DS_Store":
            total += entry.stat().st_size
    return total // 1024


def get_latest_snapshot(skill_name):
    """Get the latest snapshot tag for a skill."""
    if not LOCAL_REPO.exists():
        return None
    
    code, stdout, _ = run_cmd(
        f'git -C "{LOCAL_REPO}" tag -l "{skill_name}/v*"',
        capture=True
    )
    if code != 0 or not stdout.strip():
        return None
    
    tags = sorted(stdout.strip().split("\n"), key=lambda v: int(v.split("/v")[-1]) if "v" in v else 0)
    return tags[-1] if tags else None


# ============================================================================
# INIT COMMAND
# ============================================================================

def init_repo():
    """Initialize private GitHub repository for snapshots."""
    if not check_gh_available():
        return
    
    github_user = get_github_user()
    if not github_user:
        print("错误: 无法获取 GitHub 用户信息")
        return
    
    print("=== Skill Snapshot 初始化 ===\n")
    
    # Check if GitHub repo exists
    code, _, _ = run_cmd(f'"{GH_CMD}" repo view "{github_user}/{REPO_NAME}"')
    
    if code == 0:
        print(f"✓ GitHub 仓库已存在: {github_user}/{REPO_NAME}")
    else:
        print(f"→ 创建私有仓库: {github_user}/{REPO_NAME}")
        code, _, stderr = run_cmd(
            f'"{GH_CMD}" repo create "{REPO_NAME}" --private --description "OpenCode Skills Snapshots (私有备份)" --clone=false'
        )
        if code != 0:
            print(f"错误: 无法创建仓库: {stderr}")
            return
        print("✓ 私有仓库已创建")
    
    # Check local repo
    if LOCAL_REPO.exists() and (LOCAL_REPO / ".git").exists():
        print(f"✓ 本地仓库已存在: {LOCAL_REPO}")
        run_cmd(f'git -C "{LOCAL_REPO}" pull origin main')
    else:
        print(f"→ 克隆到本地: {LOCAL_REPO}")
        
        # Check if repo is empty
        code, stdout, _ = run_cmd(
            f'"{GH_CMD}" repo view "{github_user}/{REPO_NAME}" --json isEmpty -q ".isEmpty"'
        )
        is_empty = code == 0 and "true" in stdout.lower()
        
        if is_empty:
            LOCAL_REPO.mkdir(parents=True, exist_ok=True)
            run_cmd(f'git -C "{LOCAL_REPO}" init')
            run_cmd(f'git -C "{LOCAL_REPO}" remote add origin "https://github.com/{github_user}/{REPO_NAME}.git"')
            
            # Create README
            readme_content = """# Skill Snapshots

OpenCode 技能快照私有备份仓库。

## 结构

每个技能对应一个目录，使用 Git tags 管理版本：

```
├── <skill-name>/
│   ├── SKILL.md
│   └── scripts/
```

Tags 格式: `<skill-name>/v<n>`

## 使用

此仓库由 `skill-snapshot` 技能自动管理，请勿手动修改。
"""
            (LOCAL_REPO / "README.md").write_text(readme_content)
            run_cmd(f'git -C "{LOCAL_REPO}" add README.md')
            run_cmd(f'git -C "{LOCAL_REPO}" commit -m "Initial commit"')
            run_cmd(f'git -C "{LOCAL_REPO}" branch -M main')
            run_cmd(f'git -C "{LOCAL_REPO}" push -u origin main')
            print("✓ 仓库已初始化")
        else:
            run_cmd(f'git clone "https://github.com/{github_user}/{REPO_NAME}.git" "{LOCAL_REPO}"')
            print("✓ 已克隆到本地")
    
    print(f"\n=== 初始化完成 ===")
    print(f"私有仓库: https://github.com/{github_user}/{REPO_NAME}")
    print(f"本地路径: {LOCAL_REPO}")


# ============================================================================
# SAVE COMMAND
# ============================================================================

def save_skill(skill_name, message=None):
    """Save a skill snapshot to GitHub."""
    if not ensure_skill_dir():
        return
    
    if not check_gh_available():
        return
    
    if not LOCAL_REPO.exists() or not (LOCAL_REPO / ".git").exists():
        print("错误: 仓库未初始化，请先执行 init")
        return
    
    skill_path = SKILL_DIR / skill_name
    
    # Check skill exists
    if not skill_path.exists():
        print(f"错误: 技能不存在: {skill_path}")
        return
    
    # Check not a symlink
    if skill_path.is_symlink():
        print(f"错误: {skill_name} 是符号链接（外部安装），不支持快照")
        return
    
    # Pull latest
    run_cmd(f'git -C "{LOCAL_REPO}" pull origin main')
    run_cmd(f'git -C "{LOCAL_REPO}" fetch --tags')
    
    # Determine next version
    code, stdout, _ = run_cmd(
        f'git -C "{LOCAL_REPO}" tag -l "{skill_name}/v*"',
        capture=True
    )
    existing_tags = stdout.strip().split("\n") if stdout.strip() else []
    
    if not existing_tags or existing_tags[0] == "":
        next_version = "v1"
    else:
        versions = [int(t.split("/v")[-1]) for t in existing_tags if t]
        next_version = f"v{max(versions) + 1}"
    
    tag_name = f"{skill_name}/{next_version}"
    
    # Default message
    if not message:
        message = f"Snapshot at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    print("=== 保存快照 ===")
    print(f"技能: {skill_name}")
    print(f"版本: {next_version}")
    print(f"说明: {message}")
    print()
    
    # Copy skill directory (exclude .git, __pycache__, .DS_Store)
    dest_path = LOCAL_REPO / skill_name
    if dest_path.exists():
        shutil.rmtree(dest_path)
    dest_path.mkdir(parents=True)
    
    for item in skill_path.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(skill_path)
            # Skip certain files
            if any(part in [".git", "__pycache__", ".DS_Store", "node_modules", ".venv"] for part in rel_path.parts):
                continue
            dest_file = dest_path / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest_file)
    
    # Git add
    run_cmd(f'git -C "{LOCAL_REPO}" add "{skill_name}/"')
    
    # Check if there are changes
    code, stdout, _ = run_cmd(f'git -C "{LOCAL_REPO}" diff --cached --quiet')
    if code == 0:
        print("✓ 无变化 - 内容与最新快照相同，无需保存")
        latest = get_latest_snapshot(skill_name)
        if latest:
            print(f"→ 最新快照: {latest}")
        return
    
    # Commit and push
    run_cmd(f'git -C "{LOCAL_REPO}" commit -m "[{skill_name}] {next_version}: {message}"')
    run_cmd(f'git -C "{LOCAL_REPO}" tag -a "{tag_name}" -m "{message}"')
    run_cmd(f'git -C "{LOCAL_REPO}" push origin main')
    run_cmd(f'git -C "{LOCAL_REPO}" push origin "{tag_name}"')
    
    print(f"✓ 快照已保存: {tag_name}")
    print(f"→ 可用 'restore {skill_name} {next_version}' 恢复")


# ============================================================================
# RESTORE COMMAND
# ============================================================================

def restore_skill(skill_name, version=None):
    """Restore a skill from snapshot."""
    if not ensure_skill_dir():
        return
    
    if not check_gh_available():
        return
    
    if not LOCAL_REPO.exists() or not (LOCAL_REPO / ".git").exists():
        print("错误: 仓库未初始化，请先执行 init")
        return
    
    # Pull latest
    run_cmd(f'git -C "{LOCAL_REPO}" pull origin main')
    run_cmd(f'git -C "{LOCAL_REPO}" fetch --tags')
    
    # Get available versions
    code, stdout, _ = run_cmd(
        f'git -C "{LOCAL_REPO}" tag -l "{skill_name}/v*"',
        capture=True
    )
    available_tags = sorted(
        [t.strip() for t in stdout.strip().split("\n") if t.strip()],
        key=lambda v: int(v.split("/v")[-1])
    )
    
    if not available_tags:
        print(f"错误: 没有找到 {skill_name} 的快照")
        return
    
    # If no version specified, list available versions
    if not version:
        print(f"=== {skill_name} 可用版本 ===\n")
        for tag in available_tags:
            ver = tag.split("/")[-1]
            # Get commit message and date
            code, msg, _ = run_cmd(f'git -C "{LOCAL_REPO}" tag -l "{tag}" -n1', capture=True)
            msg = msg.replace(tag, "").strip() if msg else ""
            code, date, _ = run_cmd(
                f'git -C "{LOCAL_REPO}" log -1 --format="%ci" "{tag}"',
                capture=True
            )
            date = date.strip().split()[0] if date.strip() else ""
            print(f"  {ver} - {date} - {msg}")
        print(f"\n请指定要恢复的版本，如: restore {skill_name} v2")
        return
    
    tag_name = f"{skill_name}/{version}"
    
    # Check version exists
    if tag_name not in available_tags:
        print(f"错误: 版本不存在: {tag_name}")
        print("可用版本:")
        for t in available_tags:
            print(f"  {t.split('/')[-1]}")
        return
    
    skill_path = SKILL_DIR / skill_name
    
    # Check not a symlink
    if skill_path.exists() and skill_path.is_symlink():
        print(f"错误: {skill_name} 是符号链接（外部安装），不支持恢复")
        return
    
    print("=== 恢复快照 ===")
    print(f"技能: {skill_name}")
    print(f"版本: {version}")
    print()
    
    # Backup current version if exists
    if skill_path.exists():
        backup_dir = SKILL_DIR / ".snapshot-backup"
        backup_dir.mkdir(exist_ok=True)
        backup_name = f"{skill_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copytree(skill_path, backup_dir / backup_name)
        print(f"→ 当前版本已备份到: .snapshot-backup/{backup_name}")
    
    # Checkout to tag
    run_cmd(f'git -C "{LOCAL_REPO}" checkout "{tag_name}"')
    
    # Copy to skills directory
    if skill_path.exists():
        shutil.rmtree(skill_path)
    skill_path.mkdir(parents=True)
    
    snapshot_path = LOCAL_REPO / skill_name
    if snapshot_path.exists():
        for item in snapshot_path.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(snapshot_path)
                if ".git" in rel_path.parts:
                    continue
                dest_file = skill_path / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest_file)
    
    # Checkout back to main
    run_cmd(f'git -C "{LOCAL_REPO}" checkout main')
    
    print(f"✓ 已恢复到 {tag_name}")
    print(f"→ 技能位置: {skill_path}")


# ============================================================================
# LIST COMMAND
# ============================================================================

def list_snapshots(skill_name=None):
    """List all snapshots or for a specific skill."""
    if not check_gh_available():
        return
    
    if not LOCAL_REPO.exists() or not (LOCAL_REPO / ".git").exists():
        print("错误: 仓库未初始化，请先执行 init")
        return
    
    # Fetch latest tags
    run_cmd(f'git -C "{LOCAL_REPO}" fetch --tags')
    
    if not skill_name:
        # List all skills
        print("=== 所有技能快照 ===\n")
        
        code, stdout, _ = run_cmd(
            f'git -C "{LOCAL_REPO}" tag -l "*/v*"',
            capture=True
        )
        
        if not stdout.strip():
            print("暂无快照")
            return
        
        all_tags = [t.strip() for t in stdout.strip().split("\n") if t.strip()]
        skills = sorted(set(t.split("/")[0] for t in all_tags))
        
        for skill in skills:
            skill_tags = sorted(
                [t for t in all_tags if t.startswith(f"{skill}/")],
                key=lambda v: int(v.split("/v")[-1])
            )
            count = len(skill_tags)
            latest = skill_tags[-1].split("/")[-1] if skill_tags else "N/A"
            print(f"  {skill} ({count} 个版本, 最新: {latest})")
        
        print("\n查看特定技能: list <skill-name>")
    else:
        # List specific skill
        code, stdout, _ = run_cmd(
            f'git -C "{LOCAL_REPO}" tag -l "{skill_name}/v*"',
            capture=True
        )
        
        available_tags = sorted(
            [t.strip() for t in stdout.strip().split("\n") if t.strip()],
            key=lambda v: int(v.split("/v")[-1])
        )
        
        if not available_tags:
            print(f"没有找到 {skill_name} 的快照")
            return
        
        print(f"=== {skill_name} 快照历史 ===\n")
        
        for tag in available_tags:
            ver = tag.split("/")[-1]
            
            code, msg, _ = run_cmd(f'git -C "{LOCAL_REPO}" tag -l "{tag}" -n1', capture=True)
            msg = msg.replace(tag, "").strip() if msg else ""
            
            code, date, _ = run_cmd(
                f'git -C "{LOCAL_REPO}" log -1 --format="%ci" "{tag}"',
                capture=True
            )
            date = date.strip().split()[0] if date.strip() else ""
            
            print(f"  {ver} - {date} - {msg}")
        
        latest = available_tags[-1].split("/")[-1]
        print(f"\n最新版本: {latest}")


# ============================================================================
# DIFF COMMAND
# ============================================================================

def diff_snapshots(skill_name, version=None):
    """Diff current skill against a snapshot."""
    if not ensure_skill_dir():
        return
    
    if not check_gh_available():
        return
    
    if not LOCAL_REPO.exists() or not (LOCAL_REPO / ".git").exists():
        print("错误: 仓库未初始化，请先执行 init")
        return
    
    skill_path = SKILL_DIR / skill_name
    
    if not skill_path.exists():
        print(f"错误: 技能不存在: {skill_path}")
        return
    
    # Fetch latest tags
    run_cmd(f'git -C "{LOCAL_REPO}" fetch --tags')
    
    # Get available versions
    code, stdout, _ = run_cmd(
        f'git -C "{LOCAL_REPO}" tag -l "{skill_name}/v*"',
        capture=True
    )
    available_tags = sorted(
        [t.strip() for t in stdout.strip().split("\n") if t.strip()],
        key=lambda v: int(v.split("/v")[-1])
    )
    
    if not available_tags:
        print(f"没有找到 {skill_name} 的快照，无法对比")
        return
    
    # Determine version to compare
    if not version:
        tag_name = available_tags[-1]
        version = tag_name.split("/")[-1]
    else:
        tag_name = f"{skill_name}/{version}"
        if tag_name not in available_tags:
            print(f"错误: 版本不存在: {tag_name}")
            print("可用版本:")
            for t in available_tags:
                print(f"  {t.split('/')[-1]}")
            return
    
    print("=== 对比差异 ===")
    print(f"技能: {skill_name}")
    print(f"快照版本: {version}")
    print(f"当前版本: (本地)")
    print()
    
    # Create temp dir and checkout snapshot
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Extract snapshot to temp
        code, stdout, _ = run_cmd(
            f'git -C "{LOCAL_REPO}" archive "{tag_name}" "{skill_name}/"',
            capture=True
        )
        if code != 0:
            print(f"错误: 无法提取快照 {tag_name}")
            return
        
        # Use git archive with tar
        proc = subprocess.Popen(
            f'git -C "{LOCAL_REPO}" archive "{tag_name}" "{skill_name}/" | tar -x -C "{temp_path}"',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        proc.wait()
        
        snapshot_path = temp_path / skill_name
        
        if not snapshot_path.exists():
            print(f"错误: 快照中不存在 {skill_name} 目录")
            return
        
        # Compare
        diff_cmd = f'diff -ru "{snapshot_path}" "{skill_path}" --exclude=".DS_Store" --exclude="__pycache__"'
        code, stdout, stderr = run_cmd(diff_cmd, capture=True)
        
        if code == 0:
            print(f"✓ 无差异 - 当前版本与 {version} 相同")
        else:
            # Clean up diff output
            output = stdout.replace(str(snapshot_path), "snapshot").replace(str(skill_path), "current")
            print(output)


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Skill Snapshot - OpenCode 技能快照管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # scan
    subparsers.add_parser("scan", help="扫描技能，判断哪些需要备份")
    
    # init
    subparsers.add_parser("init", help="初始化私有 GitHub 仓库")
    
    # save
    save_parser = subparsers.add_parser("save", help="保存快照")
    save_parser.add_argument("skill", help="技能名称")
    save_parser.add_argument("message", nargs="?", help="快照说明")
    
    # restore
    restore_parser = subparsers.add_parser("restore", help="恢复快照")
    restore_parser.add_argument("skill", help="技能名称")
    restore_parser.add_argument("version", nargs="?", help="版本号")
    
    # list
    list_parser = subparsers.add_parser("list", help="列出快照")
    list_parser.add_argument("skill", nargs="?", help="技能名称")
    
    # diff
    diff_parser = subparsers.add_parser("diff", help="对比差异")
    diff_parser.add_argument("skill", help="技能名称")
    diff_parser.add_argument("version", nargs="?", help="版本号")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        print("\n=== 使用示例 ===")
        print("  skill-snapshot scan              # 扫描需要备份的技能")
        print("  skill-snapshot init               # 初始化仓库")
        print("  skill-snapshot save my-skill      # 保存快照")
        print("  skill-snapshot restore my-skill v1 # 恢复快照")
        print("  skill-snapshot list my-skill      # 列出快照")
        print("  skill-snapshot diff my-skill v1   # 对比差异")
        return
    
    # Execute command
    if args.command == "scan":
        scan_skills()
    elif args.command == "init":
        init_repo()
    elif args.command == "save":
        save_skill(args.skill, args.message)
    elif args.command == "restore":
        restore_skill(args.skill, args.version)
    elif args.command == "list":
        list_snapshots(args.skill)
    elif args.command == "diff":
        diff_snapshots(args.skill, args.version)


if __name__ == "__main__":
    main()
