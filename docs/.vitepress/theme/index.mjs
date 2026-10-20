import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import { inBrowser } from 'vitepress'
import FooterCta from './FooterCta.vue'
import './custom.css'

const SITE = 'https://yigelurenjia.com'

/** 把 /guide/a.html、/guide/a/、README 统一成 /guide/a */
function normalize(path) {
  let p = String(path || '/').replace(/\.md$/, '').replace(/\.html$/, '')
  if (!p.startsWith('/')) p = '/' + p
  if (p.length > 1) p = p.replace(/\/+$/, '')
  if (p === '/README') p = '/'
  return p || '/'
}

function ensureMeta(property, content) {
  let m = document.querySelector(`meta[property="${property}"]`)
  if (!m) {
    m = document.createElement('meta')
    m.setAttribute('property', property)
    document.head.appendChild(m)
  }
  m.setAttribute('content', content)
  return m
}

/** 每页同步 canonical 与 og:url（VitePress 不会自动做） */
function syncCanonical() {
  const full = SITE + normalize(location.pathname)

  let link = document.querySelector('link[rel="canonical"]')
  if (!link) {
    link = document.createElement('link')
    link.setAttribute('rel', 'canonical')
    document.head.appendChild(link)
  }
  link.setAttribute('href', full)

  ensureMeta('og:url', full)
}

/** 图片点击放大 */
function bindLightbox() {
  let box = document.createElement('div')
  box.id = 'lrj-lightbox'
  box.innerHTML = '<img alt=""><div class="lrj-lb-hint">点击任意处或按 Esc 关闭</div>'
  document.body.appendChild(box)

  const close = () => {
    box.classList.remove('active')
    document.body.style.overflow = ''
  }
  box.addEventListener('click', close)

  document.addEventListener('click', (e) => {
    const img = e.target && e.target.closest ? e.target.closest('.vp-doc img') : null
    if (!img || img.closest('.lrj-footer-cta')) return
    const big = box.querySelector('img')
    big.src = img.currentSrc || img.src
    big.alt = img.alt || ''
    box.classList.add('active')
    document.body.style.overflow = 'hidden'
  })

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') close()
  })
}

/** 转化事件埋点（百度统计） */
function bindTracking() {
  window.lrjTrack = function (name) {
    try {
      if (window._hmt) {
        window._hmt.push(['_trackEvent', 'convert', name, location.pathname])
      }
    } catch (err) {
      /* 统计失败不影响页面 */
    }
  }

  document.addEventListener('click', (e) => {
    const el = e.target && e.target.closest ? e.target.closest('[data-lrj-event], a') : null
    if (!el) return

    let ev = el.getAttribute('data-lrj-event')
    if (!ev && el.tagName === 'A') {
      const href = el.getAttribute('href') || ''
      if (href.indexOf('/guide/resources') === 0 || href.indexOf('./guide/resources') === 0) {
        ev = 'click_cta_resources'
      } else if (href.indexOf('xhslink') !== -1) {
        ev = 'click_buy_xhs'
      }
    }
    if (ev) window.lrjTrack(ev)
  })
}

/** 一键复制口令：execCommand 优先（兼容微信内置浏览器），再退到 Clipboard API */
function bindCopy() {
  document.addEventListener('click', (e) => {
    const btn = e.target && e.target.closest ? e.target.closest('[data-lrj-copy]') : null
    if (!btn) return
    e.preventDefault()

    const text = btn.getAttribute('data-lrj-copy') || ''
    const label = btn.textContent

    const settle = (ok) => {
      btn.textContent = ok ? '已复制，去小红书粘贴' : '复制失败，请长按选中'
      btn.classList.add(ok ? 'is-ok' : 'is-fail')
      setTimeout(() => {
        btn.textContent = label
        btn.classList.remove('is-ok', 'is-fail')
      }, 2600)
      if (ok) window.lrjTrack('click_copy_xhs')
    }

    const syncCopy = () => {
      try {
        const ta = document.createElement('textarea')
        ta.value = text
        ta.setAttribute('readonly', '')
        ta.style.position = 'fixed'
        ta.style.left = '-9999px'
        ta.style.top = '0'
        document.body.appendChild(ta)
        ta.focus()
        ta.select()
        ta.setSelectionRange(0, text.length)
        const ok = document.execCommand('copy')
        document.body.removeChild(ta)
        return ok
      } catch (err) {
        return false
      }
    }

    if (syncCopy()) {
      settle(true)
    } else if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(
        () => settle(true),
        () => settle(false)
      )
    } else {
      settle(false)
    }
  })
}

export default {
  extends: DefaultTheme,
  Layout() {
    // 文末引流块仅在文档页（doc-after）展示，首页暂不启用，后续再决定位置
    // 承接页由 FooterCta 自身逻辑跳过
    return h(DefaultTheme.Layout, null, {
      'doc-after': () => h(FooterCta)
    })
  },
  enhanceApp({ router }) {
    if (!inBrowser) return // SSG 阶段无 document
    bindLightbox()
    bindTracking()
    bindCopy()
    router.onAfterPageLoad = () => {
      syncCanonical()
    }
  }
}
