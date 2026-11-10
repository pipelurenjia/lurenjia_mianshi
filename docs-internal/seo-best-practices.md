# SEO 最佳实践（内部备忘，2026-11）

本文件只给维护者看，放在 `docs/` 外面，VitePress 不会把它编进站点。

查阅日期：2026-11-10。下面是当时仍有效的官方说法，按本站需要摘成要点。来源链接写在每节末尾。这些做法提高的是抓取、理解和展示的清晰度，不保证排名或流量。

本站是简体中文、单一语言的静态站，主域名 `https://yigelurenjia.com`。主要搜索引擎是百度、必应、Google，另外希望内容能被 AI 搜索引用。

---

## 1. title 与 description

每页都要有自己的 `<title>` 和 `<meta name="description">`。

- 标题写清这一页是什么，简短、可读，用页面正文同一种语言。不要堆关键词，不要每页只改一个词、其余全是套话。
- 全站可以在标题末尾加简短站点名，用 `|`、`-` 一类分隔。首页可以多写一句站点是做什么的，内页不要重复那一整句。
- Google 生成搜索结果标题时会同时看 `<title>`、页面上最显眼的标题（通常是第一个 H1）、`og:title` 和指向该页的锚文本。页面上如果有多个同样显眼的大标题，它可能改用别的文字。`<title>` 和页面主标题应一致。
- description 是这一页的摘要，不是全站介绍。Google 和百度都可能改写摘要，不承诺原文展示。百度移动搜索指南要求每页 description 不同，准确补充标题，不堆关键词。
- 百度清风算法打击文不对题、标题堆砌和虚假承诺。标题必须对得上正文。
- Google 不使用 `keywords` 元标签。百度现行文档讨论的是标题和摘要，不建议用 keywords 堆词。本站不加 `keywords`。
- 元信息写在静态 HTML 里。Google 不建议用 JavaScript 事后注入或改写 meta。

来源：

- [Google：影响标题链接](https://developers.google.com/search/docs/appearance/title-link)（页面标注更新于 2025-12-10）
- [Google：摘要与 meta description](https://developers.google.com/search/docs/appearance/snippet)
- [Google：支持的 meta 标签](https://developers.google.com/search/docs/crawling-indexing/special-tags)
- [Google：不使用 keywords 元标签](https://developers.google.com/search/blog/2009/09/google-does-not-use-keywords-meta-tag)
- [百度移动搜索优化指南 2.0](https://ziyuan.baidu.com/college/documentinfo?id=2085&page=2)（标题、description、图片 alt）
- [百度：清风算法与标题规范](https://ziyuan.baidu.com/college/articleinfo?id=3166)
- [百度移动搜索建站优化白皮书](https://ziyuan.baidu.com/college/articleinfo?id=1710)

## 2. 标题层级

一页一个清楚的主标题，用 H1，并和 `<title>` 对应。后面的章节用 H2、H3，不要再出现第二个 H1。

Google 把「看不出哪个是主标题」列为标题被改写的常见原因：多个标题同一层级、同样醒目时，它可能只取第一个。

正文仍按读者来组织。H2 的文字应当是这一节的小标题，而不是为了塞词。

来源：同上，[Google 标题链接](https://developers.google.com/search/docs/appearance/title-link) 中 “Make it clear which text is the main title” 与 “No clear main title”。

## 3. canonical

每页放一条指向自己的绝对 URL：

```html
<link rel="canonical" href="https://yigelurenjia.com/guide/start-here">
```

- 用最终希望被收录的地址：本站是 `https`、无 `www`、无 `.html`、目录页不带尾部斜杠（首页除外，首页是 `https://yigelurenjia.com/`）。
- 不要在 canonical、sitemap、内链之间给出不同的首选地址。
- 不要用 robots.txt 来指定规范网址。被 Disallow 的网址仍可能被编入索引，只是没有正文。
- 不要把带 `#` 片段的 URL 当作 canonical。
- canonical 写在 HTML 源码里，不要只靠前端路由改。

本站 `http://` 与 `https://www` 已 301 到 `https://yigelurenjia.com/`。这是比 canonical 更强的信号，应保持。

来源：

- [Google：规范网址](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
- [VitePress：transformHead](https://vitepress.dev/reference/site-config#transformhead)（只在构建时写入静态 HTML）

## 4. sitemap 与 lastmod

XML sitemap 只列出希望被收录的规范 URL。在 `robots.txt` 里用一行 `Sitemap:` 指向它，并在站长平台提交。sitemap 不是排名，只是发现和更新的提示。

`lastmod` 必须是该 URL 正文（或会改变搜索理解的结构化数据、主要链接）的最后一次实质性修改时间，不是生成 sitemap 的时间。格式用 ISO 8601。可以带时间。

- Google：日期必须真实。如果长期报错，Google 会不再相信这个站点的 `lastmod`。改侧栏、页脚这类不影响该页主体的文字，不必更新。改了正文、结构化数据或主要链接，应该更新。`changefreq` 和 `priority` 可以不写。
- 必应：同样忽略 `changefreq` 和 `priority`。建议带时间的 ISO 8601。`lastmod` 会用来决定要不要重新抓取，也影响 Copilot 一类体验里的新鲜度。必应同时看 HTTP 验证头（如 ETag）。
- 百度：`lastmod` 可选，格式 `YYYY-MM-DD` 或 `YYYY-MM-DDThh:mm:ss`。索引型 sitemap（只指向其他 sitemap、没有具体 URL）百度不处理。本站一个 URL 列表即可。

VitePress 在 `lastUpdated: true` 时用 `git log -1` 填 `lastmod`。浅克隆时，所有文件都会变成同一次提交的时间，线上就会失真。本仓库用 `scripts/gen-lastmod.py` 在有完整历史时写入 `docs/.vitepress/lastmod.json`，构建时优先用这份文件。浅克隆只保留已提交的 json，不用错误时间覆盖。

来源：

- [Google：建立 sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Google：lastmod 与 ping 下线](https://developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping)
- [必应：AI 搜索里的 sitemap 与 lastmod](https://blogs.bing.com/webmaster/2025/7/Keeping-Content-Discoverable-with-Sitemaps-in-AI-Powered-Search/)
- [必应站长指南](https://www.bing.com/webmasters/help/webmasters-guidelines-30fba23a)
- [百度 sitemap 格式](https://ziyuan.baidu.com/site/format)
- [百度 sitemap 说明](https://ziyuan.baidu.com/wiki/640)
- [VitePress sitemap](https://vitepress.dev/guide/sitemap-generation)
- [VitePress lastUpdated](https://vitepress.dev/reference/default-theme-last-updated)

## 5. robots.txt

robots.txt 只是抓取建议，挡不住不遵守的客户端，也不能可靠地阻止收录。不想被索引要用 `noindex`，而不是只写 Disallow。

同一爬虫有多组规则时，Google 按 [robots.txt 规范](https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt) 合并最具体的组；路径一样长时 Allow 优先于 Disallow。百度的公开说明只讲「可以告诉百度哪些能抓、哪些不能抓」，没有承诺和 Google 相同的合并方式。实践中，写在文件前面的 `User-agent` 专组经常被当作该爬虫的有效规则。因此同一爬虫前面 `Disallow: /`、后面 `Allow: /`，不能当成「后面那条一定生效」。

本站仓库里的 `docs/public/robots.txt` 是允许抓取，并声明 sitemap。线上文件开头另有一段 Cloudflare 托管的 Content Signals，那是控制台设置，不在仓库里。影响和改法见文末第 12 节。

来源：

- [Google：robots.txt 简介](https://developers.google.com/search/docs/crawling-indexing/robots/intro)
- [Google：robots.txt 规格](https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt)
- [RFC 9309](https://www.rfc-editor.org/rfc/rfc9309)
- [百度 Robots 工具说明](https://ziyuan.baidu.com/robots/intro)
- [Cloudflare：托管 robots.txt](https://developers.cloudflare.com/bots/additional-configurations/managed-robots-txt/)（文档标注更新于 2026-11-02）

## 6. 结构化数据

用 JSON-LD，字段必须和页面上看得见的内容一致。标记看不见的内容，或标记与正文不符，可能让整段结构化数据被忽略。

| 类型 | 本站是否使用 | 原因 |
| --- | --- | --- |
| `WebSite` | 只用在首页 | 描述站点名称、URL、语言。没有服务端搜索 URL，不加 `SearchAction`。 |
| `BreadcrumbList` | 用在内页 | 至少两项。本站没有栏目落地页，可见面包屑是「首页 / 当前篇」，JSON-LD 与这一条一致。最后一项可以不写 `item`，Google 会用当前页 URL。栏目名已经在侧栏里，不造一个不存在的栏目 URL。 |
| `Article` | 用在内页 | schema.org 的 Article 可以表示一篇说明文。Google 的 Article 富媒体结果主要面向新闻、博客和体育。本站标的是真实的标题、摘要、语言和作者名，不标评分、价格或联系方式。有 git 时间才写 `dateModified`，不编造 `datePublished`。配图若只是标志，不放进 `image`（Google 要求配图是内容本身，不是 logo）。 |
| `FAQPage` | 不用 | 2023-08 起，FAQ 富媒体结果只给知名的政府站和健康站。2026-05-07 起，Google 搜索不再展示 FAQ 富媒体结果，2026-06 起文档已删除。页内「常见问题」只是文章的一节，不是整页 FAQ。百度的「通用问答」要在搜索资源平台按他们的格式提交，且不保证展示；本站不代为提交。 |

面包屑富媒体结果在桌面搜索仍可能出现，移动搜索结果里 Google 已不再展示面包屑路径（2025-01 起）。标记仍然有用，只是手机结果上不一定看得见。

来源：

- [schema.org WebSite](https://schema.org/WebSite)
- [schema.org BreadcrumbList](https://schema.org/BreadcrumbList)
- [schema.org Article](https://schema.org/Article)
- [schema.org FAQPage](https://schema.org/FAQPage)
- [Google：面包屑](https://developers.google.com/search/docs/appearance/structured-data/breadcrumb)（标注更新于 2026-09-08）
- [Google：Article](https://developers.google.com/search/docs/appearance/structured-data/article)
- [Google：移动结果不再展示面包屑](https://developers.google.com/search/blog/2025/01/simplifying-breadcrumbs)
- [Google：FAQ 富媒体结果停用](https://developers.google.com/search/updates)（2026-05-08 弃用，2026-06-17 删除文档）
- [Google：2023-08 FAQ 仅限政府与健康站点](https://developers.google.com/search/blog/2023/08/howto-faq-changes)
- [百度结构化数据工具](https://ziyuan.baidu.com/wiki/721)（通用问答、在线文档、资料下载、软件下载；不保证展示）
- [必应：结构化数据与 Open Graph](https://www.bing.com/webmasters/help/marking-up-your-site-with-structured-data-3a93e731)

## 7. Open Graph

每页单独写 `og:title`、`og:description`、`og:url`，与 `<title>`、description、canonical 一致。`og:locale` 用 `zh_CN`。`og:image` 写绝对 URL，并带上宽高和 alt。本站分享图是 240×204 的标志，不是 1200×630 的大图。

首页 `og:type` 为 `website`，内页为 `article`。

必应能读 Open Graph，但是否用在结果里由必应决定，且他们写明目前主要影响部分发布者的视觉展示。微信等用 `og:` 生成转发卡片。

来源：

- [Open Graph 协议](https://ogp.me/)
- [必应结构化数据说明](https://www.bing.com/webmasters/help/marking-up-your-site-with-structured-data-3a93e731)（含 `og:image` 宽高）
- [VitePress head 合并规则](https://vitepress.dev/reference/site-config#head)（同名 meta 后者覆盖前者）

## 8. 内链

重要页面应当能从首页和栏目导航点到，锚文本写清目标页在讲什么，并链到规范 URL。百度建议站点呈「首页—栏目—正文」的浅层结构，正文页能回到首页和上级；同一 URL 的锚文本不要变成一堆互不相关的词。

Google 要求链接是可抓取的 `<a href>`，不要只放在要点击才执行的脚本里。VitePress 输出的侧栏、文末上一篇/下一篇和首页目录都是这种链接。

来源：

- [Google Search Essentials](https://developers.google.com/search/docs/essentials)
- [百度移动搜索优化指南 2.0](https://ziyuan.baidu.com/college/documentinfo?id=2085&page=2)（结构扁平、网状链接、锚文本）
- [百度移动建站白皮书：内链](https://ziyuan.baidu.com/college/articleinfo?id=1710)

## 9. 图片 alt 与尺寸

- alt 说明这张图是什么，放在相关正文旁边。不要堆关键词。装饰性图片可以用空 alt。
- 文件名尽量能看出内容。本站历史图片文件名已经固定，不为了改名去换 URL。
- HTML 上写真实的 `width` 和 `height`。CSS 若把宽度改成 100% 或固定像素，必须同时写 `height: auto`，否则浏览器会按属性高度撑开，图片变形。百度建议非文字元素指定宽高，避免重排。这也直接关系 CLS。
- 标志不要冒充文章配图放进 Article 的 `image`。

来源：

- [Google 图片最佳实践](https://developers.google.com/search/docs/appearance/google-images)
- [百度移动搜索优化指南 2.0](https://ziyuan.baidu.com/college/documentinfo?id=2085&page=2)（alt）
- [百度落地页体验：首屏与宽高](https://ziyuan.baidu.com/college/articleinfo?id=1710)

## 10. 性能与 Core Web Vitals

Google 建议把真实用户的三项指标保持在：

- LCP 2.5 秒以内
- INP 200 毫秒以内
- CLS 0.1 以内

这是页面体验的一部分，不是单独的排名承诺。百度移动文档建议首屏尽快出来，CSS 放前面，脚本异步或置后，图片给出宽高；他们引用的体验白皮书把「首屏 1 秒内」当作留存更好的区间，同样不是排名保证。

静态 HTML 已经避免「正文等 JS 才出现」。本站还能做的是：图片占位、对已经使用的第三方统计域名做 `preconnect`、不新增阻塞脚本。已有的百度统计和 Cloudflare Analytics 是现有功能，不在这次去掉。

来源：

- [Google：Core Web Vitals](https://developers.google.com/search/docs/appearance/core-web-vitals)
- [Google：给开发者的 SEO 起点](https://developers.google.com/search/docs/fundamentals/get-started)
- [百度移动建站白皮书：访问速度](https://ziyuan.baidu.com/college/articleinfo?id=1710)

## 11. 移动端、语言与 hreflang

- 有 viewport，一套响应式页面同时给电脑和手机。百度说明：自适应站点不需要提交「移动适配」工具。可加 `<meta name="applicable-device" content="pc,mobile">`，表示这一页电脑和手机都能看。
- 只有简体中文一种版本。`hreflang` 是用来声明同一内容的其他语言或地区 URL 的。没有第二种 URL，就不要加 `hreflang`。
- `<html lang="zh-CN">` 对浏览器和辅助技术有用。Google 写明：他们不靠 `lang` 或 `hreflang` 判断页面语言，而是看可见正文。页面上的标题、导航和正文保持同一种语言即可。
- 不要做只翻译导航、正文仍是另一种语言的页面。

来源：

- [Google：本地化版本与 hreflang](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Google：多地区与多语言站点](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)
- [百度：自适应站点不用移动适配](https://ziyuan.baidu.com/mobile/index)
- [百度移动搜索优化指南 2.0](https://ziyuan.baidu.com/college/documentinfo?id=2085&page=2)（`applicable-device`）
- [VitePress：`lang`](https://vitepress.dev/reference/site-config#lang)

## 12. IndexNow，以及线上 robots 被 Cloudflare 改写

### IndexNow

IndexNow 用来通知参与该协议的引擎：某个 URL 新增、更新或删除了。它不保证被抓取或收录。一次提交会在参与方之间共享。公开名单里有必应、Yandex、Seznam、Naver 等。Google 和百度不在其中。对这个站，IndexNow 只覆盖必应（以及使用同一协议的引擎），不能代替百度普通收录或 Google Search Console。

自己接入需要一把密钥，并在网站上放置密钥文件，再用 `https://api.indexnow.org/indexnow` 提交变更的 URL。不要每天把全站重复提交一遍。密钥属于需要保管的凭据，本仓库不写入、也不代为提交。

若不想在仓库放密钥，Cloudflare 的 Crawler Hints 会在缓存未命中、认为内容变了时代为通知 IndexNow。打开位置见 [Crawler Hints 文档](https://developers.cloudflare.com/cache/advanced-configuration/crawler-hints/)：仪表盘的 Configuration 页。这是账号里的开关，不是仓库配置。开启后仍然不保证收录，也不通知百度和 Google。

来源：

- [IndexNow 文档](https://www.indexnow.org/documentation)
- [必应：如何添加 IndexNow](https://www.bing.com/indexnow/getstarted)
- [必应站长指南：URL 变更通知](https://www.bing.com/webmasters/help/webmasters-guidelines-30fba23a)
- [Cloudflare Crawler Hints](https://developers.cloudflare.com/cache/advanced-configuration/crawler-hints/)

### 线上 robots.txt 与百度、AI 爬虫

2026-11-10 请求 `https://yigelurenjia.com/robots.txt`，文件开头是 Cloudflare 托管内容，然后再接仓库里的原文。托管段包含：

- `Content-Signal: search=yes,ai-train=no,use=reference`
- 对一批爬虫 `Disallow: /`，其中有 `Baiduspider`、`GPTBot`、`ClaudeBot`、`Bytespider`、`GoogleOther`、`Google-Extended`、`CCBot` 等

`Content-Signal` 不是 RFC 9309 的指令。Cloudflare 的定义是：`search` 指建立搜索索引和展示链接与短摘录，明确不包括 AI 生成的搜索摘要；`ai-input` 指把内容送进模型做实时回答；`ai-train` 指训练。当前托管值是允许传统搜索索引、不允许训练、使用方式为引用。Google Search Console 有时会对 Content-Signal 报「语法无法识别」。Cloudflare 写明他们观察到这句警告本身没有改变抓取量。真正会改变抓取的是下面的 `Disallow`。

影响：

- `Baiduspider` 被整站 `Disallow: /`。仓库后文又写了 `Allow: /`。若百度采用文件中先出现的专组，等于告诉百度蜘蛛不要抓。这是中文站最大的实际风险。百度 AI 搜索用的也是百度蜘蛛体系，会一起受影响。
- `Googlebot` 和 `bingbot` 不在托管的 Disallow 名单里，仓库的 `User-agent: *` 是 `Allow: /`。常规的 Google 搜索和必应搜索抓取没有被这段名单关掉。
- `Google-Extended` 是 Gemini / Vertex 训练的控制令牌，Disallow 它不等于禁止 Google 搜索收录。
- `GoogleOther` 不是主搜索蜘蛛 `Googlebot`。仓库里写的是 `Google-Other`（多了一个连字符），对不上 Google 公布的令牌 `GoogleOther`，所以仓库里的那条 Allow 并不会抵消托管段的 Disallow。
- `GPTBot`、`ClaudeBot`、`Bytespider`、`CCBot` 等被 Disallow。仓库后文的 Allow 与前面的 Disallow 冲突，不能假设后文生效。这会减少这些系统把本站当作训练或抓取来源的机会。`ChatGPT-User`、`PerplexityBot` 不在托管 Disallow 名单里。
- 托管段的 `search=yes` 只是 Content-Signal 声明，取消不了同一文件里对 `Baiduspider` 的 `Disallow: /`。

怎么改（在 Cloudflare 控制台，不要改仓库来「对抗」这段前缀）：

1. 打开该域名的 Cloudflare 仪表盘，进入 Security → Settings，筛选 Bot traffic。
2. 打开 AI Crawler and Agent access policies。
3. 若希望线上 robots 恢复成仓库原文：把 Search、Agent、Training 都设为允许，并关闭 Enable Bot Preference Sync。Cloudflare 写明：只有 Bot Preference Sync 开启，且至少一项策略是 Block、Block on pages with ads，或 Training 为 Disallow 时，才会把托管段加到现有 robots.txt 前面。全部允许时，返回的就是源站文件。
4. 保存后几秒内刷新 `https://yigelurenjia.com/robots.txt` 确认开头不再是 `# BEGIN Cloudflare Managed content`。文档写明不需要单独清缓存。
5. 托管名单不能逐条编辑。若仍想禁止一部分训练爬虫，但必须允许 `Baiduspider`，应关掉托管段，再在仓库的 robots.txt 里只写下真正要限制的 User-agent。不要把 `Baiduspider` 写进 Disallow。

来源：

- [Cloudflare 托管 robots.txt](https://developers.cloudflare.com/bots/additional-configurations/managed-robots-txt/)
- [Cloudflare AI 爬虫访问策略](https://developers.cloudflare.com/bots/additional-configurations/block-ai-bots/)
- 线上文件：`https://yigelurenjia.com/robots.txt`（2026-11-10 抓取）

## 13. AI 搜索引用

Google 在 2026-05 的生成式搜索指南里写明：AI 概览和 AI 模式用的仍是搜索索引。页面要能被正常抓取、索引，并允许摘要。技术要求和普通搜索相同。没有单独的「给 AI 的标记」可以提高 Google 收录。

同一指南和 2026-06 的文档更新写明：`llms.txt` 不是 Google 搜索需要的文件，保留它不会提高也不会降低 Google 搜索中的表现。本站继续提供 `/llms.txt` 和 `/llms-full.txt`，给其他会读这个文件的系统用。正文以静态 HTML 为准。

想出现在生成式结果里，Google 强调的是人能读懂的、有自己观点的内容，而不是按问法批量造页。那属于内容本身，不是这次技术改动要改写的东西。

必应把 sitemap 的 `lastmod` 和 IndexNow 都描述为 Copilot 可用的新鲜度信号，同样不保证被引用。

来源：

- [Google：面向生成式搜索功能的优化](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- [Google：该指南的发布说明](https://developers.google.com/search/blog/2026/05/a-new-resource-for-optimizing)
- [Google 文档更新：llms.txt 不影响 Google 搜索](https://developers.google.com/search/updates)（2026-06-15）
- [必应：sitemap 与 AI 搜索](https://blogs.bing.com/webmaster/2025/7/Keeping-Content-Discoverable-with-Sitemaps-in-AI-Powered-Search/)

## 14. 本站实现时采用的对应关系

| 做法 | 落点 |
| --- | --- |
| 每页 title / description | Markdown frontmatter。title 与该页 H1 相同，不改侧栏文字 |
| canonical、og:url、og:title、og:description | `docs/.vitepress/config.mjs` 的 `transformHead` |
| 面包屑 JSON-LD 与可见导航 | 同一套「首页 / 当前篇」 |
| sitemap lastmod | `scripts/gen-lastmod.py` → `docs/.vitepress/lastmod.json` |
| 一个 H1 | 只把第二个 H1 降为 H2，文字不动 |
| 首页目录 | 与侧栏条目对齐，补上缺失链接 |
| 侧栏「关于我」 | 主题插槽，不再依赖 Docsify 的 `_sidebar.md` |
| FAQPage、IndexNow 密钥、搜索引擎提交 | 不做 |
