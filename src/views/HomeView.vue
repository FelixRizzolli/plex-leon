<script setup lang="ts">
import { useAppStore } from '@stores/app'

const appStore = useAppStore()
</script>

<template>
  <div class="home-view">
    <h1 class="page-title">Welcome to <span class="text-accent">plex-leon</span></h1>
    <p class="page-sub text-muted">Electron · Vue 3.6 Vapor · Vite 8 · Pinia · TypeScript</p>

    <div class="grid">
    </div>
  </div>
</template>

<style scoped>
.home-view { max-width: 900px; }
.page-title { font-size: 24px; font-weight: 700; margin-bottom: 6px; }
.page-sub { margin-bottom: 28px; }

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}



.info-grid {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 6px 12px;
}
.info-grid dt { color: var(--color-text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
.info-grid dd { color: var(--color-text); font-size: 13px; }
</style>
