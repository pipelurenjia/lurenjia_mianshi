import { defineConfig } from 'vitepress'

const SITE = 'https://yigelurenjia.com'
const TITLE = '一个路人甲 · 结构化面试'
const FULL_TITLE = '一个路人甲 · 结构化面试原创学习体系 | 免费自学资料'
const DESCRIPTION =
  '免费、系统、实战的结构化面试自学知识体系。从零基础到上岸的完整学习路径，包含布点法、观点展开法、问答笔记法等原创方法论，覆盖综合分析、组织管理、应急应变等各类题型。'

export default defineConfig({
  title: TITLE,
  // 页面标题统一成「文章标题 | 站点名」，与 Docsify 时代保持一致
  titleTemplate: ':title | 一个路人甲 · 结构化面试',
  description: DESCRIPTION,
  lang: 'zh-CN',

  // 关键：输出 /guide/start-here 而不是 /guide/start-here.html
  // 保证 36 个 URL 与 Docsify 时代完全一致，收录不丢
  cleanUrls: true,

  // 构建产物输出到仓库根目录的 dist/（便于 Cloudflare Pages 直接指定）
  outDir: '../dist',

  lastUpdated: true,

  head: [
    ['link', { rel: 'icon', href: '/favicon.ico', sizes: 'any' }],
    ['link', { rel: 'icon', type: 'image/png', sizes: '32x32', href: '/assets/img/favicon-32x32.png' }],
    ['link', { rel: 'icon', type: 'image/png', sizes: '16x16', href: '/assets/img/favicon-16x16.png' }],
    ['link', { rel: 'apple-touch-icon', sizes: '180x180', href: '/assets/img/apple-touch-icon.png' }],
    ['link', { rel: 'manifest', href: '/site.webmanifest' }],
    ['meta', { name: 'theme-color', content: '#348f6b' }],

    // 分享卡片（微信 / 小红书 / 群聊转发时的标题与缩略图）
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:site_name', content: TITLE }],
    ['meta', { property: 'og:title', content: FULL_TITLE }],
    ['meta', { property: 'og:description', content: DESCRIPTION }],
    ['meta', { property: 'og:image', content: `${SITE}/assets/img/logo.png` }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }],

    // canonical / og:url 由下方 transformHead 在构建期逐页写入

    // 百度统计（静态标签，便于百度校验工具识别）
    ['script', {}, 'var _hmt = _hmt || [];'],
    ['script', { async: true, src: 'https://hm.baidu.com/hm.js?2cca587794a1cfb3a439deb6a43fa2e2' }],

    // Cloudflare Web Analytics
    [
      'script',
      {
        type: 'module',
        src: 'https://static.cloudflareinsights.com/beacon.min.js',
        'data-cf-beacon': '{"token": "cfa482f444494871a502b7267648409d", "spa": true}'
      }
    ]
  ],

  themeConfig: {
    nav: [
      { text: '从零开始', link: '/guide/start-here' },
      { text: '资料与课程', link: '/guide/resources' }
    ],

    // 与 _sidebar.md 完全一致的 7 个分类、35 个条目
    sidebar: [
      {
        text: '我是小白',
        items: [
          { text: '从零开始怎么学', link: '/guide/start-here' },
          { text: '游击战法：快速入门', link: '/guide/guerrilla' },
          { text: '上考场急救包', link: '/guide/emergency' },
          { text: '面试班选择指南', link: '/guide/choose-class' }
        ]
      },
      {
        text: '答题方法论',
        items: [
          { text: '布点法：如何快速破题', link: '/method/point-method' },
          { text: '观点展开：怎么说清楚', link: '/method/expand' },
          { text: '观点展开法：完整版', link: '/method/point-expand' },
          { text: '广度深度：展不开怎么办', link: '/method/breadth-depth' },
          { text: '化虚为实：避免车轱辘话', link: '/method/concrete' },
          { text: '答题同质化怎么破', link: '/method/break-homogenization' },
          { text: '提高深度：洞察事物内在联系', link: '/method/improve-depth' },
          { text: '宏观练习：大量答题把握规律', link: '/method/practice-macro' }
        ]
      },
      {
        text: '题型专训',
        items: [
          { text: '综合分析题', link: '/question-types/comprehensive' },
          { text: '组织管理题', link: '/question-types/organization' },
          { text: '应急应变题', link: '/question-types/emergency' },
          { text: '人际关系题', link: '/question-types/relationship' },
          { text: '情景模拟题', link: '/question-types/simulation' },
          { text: '态度观点题怎么答', link: '/question-types/attitude-viewpoint' },
          { text: '即兴演讲题怎么答', link: '/question-types/impromptu-speech' },
          { text: '漫画名言哲理题', link: '/question-types/allegory' },
          { text: '调研类题目', link: '/question-types/research' }
        ]
      },
      {
        text: '练习方法',
        items: [
          { text: '复盘方法论', link: '/practice/review' },
          { text: '高效练习方法', link: '/practice/practice-methods' },
          { text: '问答笔记法详解', link: '/practice/note-taking-deep' },
          { text: '复述法详解', link: '/practice/repeat-deep' },
          { text: '对练方法', link: '/practice/practice-with-others' }
        ]
      },
      {
        text: '表达能力',
        items: [
          { text: '口头语消除训练', link: '/expression/stop-words' },
          { text: '口语化表达', link: '/expression/spoken-style' },
          { text: '流畅性训练', link: '/expression/fluency' }
        ]
      },
      {
        text: '心态调整',
        items: [
          { text: '考场紧张怎么办', link: '/mindset/nervous' },
          { text: '焦虑缓解方法', link: '/mindset/anxiety' },
          { text: '备考节奏把控', link: '/mindset/pace' },
          { text: '备考厌学怎么办', link: '/mindset/study-fatigue' },
          { text: '心态答疑：坚持还是放弃', link: '/mindset/mindset' }
        ]
      },
      {
        text: '资料与课程',
        items: [
          { text: '配套资料与视频课', link: '/guide/resources' }
        ]
      }
    ],

    // 中文界面文案
    outline: { level: [2, 3], label: '本页目录' },
    docFooter: { prev: '上一篇', next: '下一篇' },
    lastUpdated: { text: '最后更新于' },
    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '目录',
    darkModeSwitchLabel: '主题',
    lightModeSwitchTitle: '切换到浅色模式',
    darkModeSwitchTitle: '切换到深色模式',
    outlineTitle: '本页目录',

    // 站内搜索（本地索引，构建时生成，无需外部服务）
    search: {
      provider: 'local',
      options: {
        locales: {
          root: {
            translations: {
              button: { buttonText: '搜索', buttonAriaLabel: '搜索' },
              modal: {
                noResultsText: '没有找到结果',
                resetButtonTitle: '清除查询条件',
                footer: {
                  selectText: '选择',
                  navigateText: '切换',
                  closeText: '关闭'
                }
              }
            }
          }
        }
      }
    },

    socialLinks: [],

    footer: {
      message: '本作品采用 CC BY-NC-SA 4.0 许可证进行许可。',
      copyright: '版权所有 © 2026 路人甲'
    },

    editLink: null
  },

  sitemap: {
    hostname: SITE
  },

  // 关键：构建期就为每一页写入正确的 canonical / og:url
  // 否则 36 个页面会共用首页的 canonical，等于互相重复
  transformHead({ pageData }) {
    let clean = String(pageData.relativePath || '')
      .replace(/\.md$/, '')
      .replace(/(^|\/)index$/, '')
    if (!clean.startsWith('/')) clean = '/' + clean
    const url = SITE + (clean === '/' ? '/' : clean)

    return [
      ['link', { rel: 'canonical', href: url }],
      ['meta', { property: 'og:url', content: url }],
      ['meta', { property: 'og:title', content: `${pageData.title} | 一个路人甲 · 结构化面试` }]
    ]
  }
})
