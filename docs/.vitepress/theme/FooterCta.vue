<script setup>
import { computed } from 'vue'
import { useRoute, withBase } from 'vitepress'

const route = useRoute()
const logoSrc = withBase('/assets/img/logo.png')

// 承接页自身不再注入（与 Docsify 版行为一致）
const show = computed(() => (route.path || '').indexOf('resources') === -1)
</script>

<template>
  <div v-if="show" class="lrj-footer-cta">
    <img :src="logoSrc" alt="一个路人甲" />
    <div class="lrj-cta-text">
      <p class="lrj-cta-title">配套资料与视频课</p>
      <p class="lrj-cta-sub">思维总结 · 答题示例 · 视频课，网站内容之外更系统的整理</p>
    </div>
    <a class="lrj-cta-link" :href="withBase('/guide/resources')">查看</a>
  </div>
</template>
