import cv2
import numpy as np
import os
from PIL import Image

SRC_DIR = r"D:\Coding\lurenjia_mianshi\小红书公众号二维码及商品图片"
GOODS = r"D:\Coding\一个路人甲小红书素材库\Goods_Images_商品图片"
OUT_DIR = r"D:\Coding\lurenjia_mianshi\assets\img"
os.makedirs(OUT_DIR, exist_ok=True)

detector = cv2.QRCodeDetector()

def imread_cn(path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)

def crop_qr(src_path, out_path, bbox, pad_ratio=0.18, border=28, size=340):
    img = imread_cn(src_path)
    h, w = img.shape[:2]
    (x1, y1), (x2, y2) = bbox
    pw, ph = (x2 - x1), (y2 - y1)
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    half = int(max(pw, ph) * (1 + pad_ratio) / 2) + 6
    x1c, y1c = max(0, cx - half), max(0, cy - half)
    x2c, y2c = min(w, cx + half), min(h, cy + half)
    crop = img[y1c:y2c, x1c:x2c]
    # validate: QR still detectable in crop
    ok, _, _ = detector.detectAndDecode(crop)[0], None, None
    data2, pts2, _ = detector.detectAndDecode(crop)
    # pad with white border
    crop_pil = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
    padded = Image.new("RGB", (crop_pil.width + border * 2, crop_pil.height + border * 2), (255, 255, 255))
    padded.paste(crop_pil, (border, border))
    # resize to target square-ish
    side = max(padded.size)
    sq = Image.new("RGB", (side, side), (255, 255, 255))
    sq.paste(padded, ((side - padded.width) // 2, (side - padded.height) // 2))
    sq = sq.resize((size, size), Image.LANCZOS)
    sq.save(out_path, optimize=True)
    kb = os.path.getsize(out_path) / 1024
    print(f"saved {out_path} ({kb:.0f} KB) qr_recheck={'OK' if pts2 is not None else 'FAIL'}")

def compress_img(src_path, out_path, max_w=800, quality=82):
    img = Image.open(src_path)
    if img.mode in ("RGBA", "P"):
        alpha = img.mode == "RGBA"
        if out_path.endswith(".jpg"):
            img = img.convert("RGB")
    if img.width > max_w:
        ratio = max_w / img.width
        img = img.resize((max_w, int(img.height * ratio)), Image.LANCZOS)
    if out_path.endswith(".jpg"):
        img.save(out_path, quality=quality, optimize=True)
    else:
        img.save(out_path, optimize=True)
    kb = os.path.getsize(out_path) / 1024
    print(f"saved {out_path} ({img.width}x{img.height}, {kb:.0f} KB)")

# 1. XHS QR from 微信图片_20261019132626_4_7.jpg bbox (690,1050)-(908,1249)
crop_qr(
    os.path.join(SRC_DIR, "微信图片_20261019132626_4_7.jpg"),
    os.path.join(OUT_DIR, "xhs-qr.png"),
    ((690, 1050), (908, 1249)),
)

# 2. WeChat QR from 微信图片_20261019143549_86_4.jpg bbox (155,387)-(686,906)
crop_qr(
    os.path.join(SRC_DIR, "微信图片_20261019143549_86_4.jpg"),
    os.path.join(OUT_DIR, "wechat-qr.png"),
    ((155, 387), (686, 906)),
)

# 3. Video course images
vdir = os.path.join(GOODS, "02结构化面试视频课介绍图片")
compress_img(os.path.join(vdir, "主图.png"), os.path.join(OUT_DIR, "course-main.jpg"))
compress_img(os.path.join(vdir, "01绪论+02方法论.jpg"), os.path.join(OUT_DIR, "course-chapters.jpg"))
compress_img(os.path.join(vdir, "上课思维导图-训练方法.png"), os.path.join(OUT_DIR, "course-mindmap.jpg"))

# 4. Materials images
mdir = os.path.join(GOODS, "01结构化面试文字资料合集截图")
compress_img(os.path.join(mdir, "01思维总结.jpg"), os.path.join(OUT_DIR, "materials-cover.jpg"))
compress_img(os.path.join(mdir, "01思维总结-目录.png"), os.path.join(OUT_DIR, "materials-toc.jpg"))

# 5. Logo
compress_img(r"D:\Coding\lurenjia_mianshi\LOGO_抠图.png", os.path.join(OUT_DIR, "logo.png"), max_w=240)
