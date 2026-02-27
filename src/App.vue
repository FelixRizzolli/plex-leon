<script setup lang="ts">
import { onMounted } from 'vue'
import { useAppStore } from '@stores/app'
import AppLayout from '@components/layout/AppLayout.vue'

const appStore = useAppStore()

onMounted(() => {
  appStore.init()
  // Apply saved theme on first render
  document.documentElement.setAttribute('data-theme', appStore.theme)
})
</script>

<template>
  <AppLayout />
</template>
