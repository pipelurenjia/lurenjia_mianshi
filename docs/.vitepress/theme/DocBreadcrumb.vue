<script setup>
import { computed } from 'vue'
import { useData, withBase } from 'vitepress'

const { page, frontmatter } = useData()

const show = computed(() => frontmatter.value.layout !== 'home')
const label = computed(() => page.value.title || frontmatter.value.title || '')
const homeHref = withBase('/')
</script>

<template>
  <nav v-if="show && label" class="lrj-breadcrumb" aria-label="面包屑">
    <a :href="homeHref">首页</a>
    <span aria-hidden="true">/</span>
    <span aria-current="page">{{ label }}</span>
  </nav>
</template>
