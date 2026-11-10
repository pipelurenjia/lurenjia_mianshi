<script setup>
import { withBase } from 'vitepress'

const logoSrc = withBase('/assets/img/logo.png')
const resourcesHref = withBase('/guide/resources')
</script>

<template>
  <div class="lrj-side-card">
    <img :src="logoSrc" width="240" height="204" alt="一个路人甲标志" />
    <p class="lrj-side-name">一个路人甲</p>
    <p class="lrj-side-desc">自学面试93分上岸 · 小红书 @pipelurenjia</p>
    <a class="lrj-side-btn" :href="resourcesHref">资料与课程 →</a>
  </div>
</template>
