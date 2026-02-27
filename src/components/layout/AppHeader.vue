<script setup lang="ts">
import { useAppStore } from '@stores/app'

const appStore = useAppStore()
</script>

<template>
  <header class="app-header">
    <!-- Electron drag region -->
    <div class="drag-region" />

    <div class="header-left">
      <button class="sidebar-toggle" title="Toggle sidebar" @click="appStore.toggleSidebar()">
        <span class="icon">☰</span>
      </button>
      <span class="app-name">{{ appStore.appInfo?.name ?? 'plex-leon' }}</span>
    </div>

    <div class="header-right">
      <span class="version text-muted text-sm">
        v{{ appStore.appInfo?.version ?? '…' }}
      </span>
      <button class="icon-btn" title="Toggle theme" @click="appStore.toggleTheme()">
        {{ appStore.isDark ? '☀️' : '🌙' }}
      </button>

      <!-- Custom window controls (frameless) -->
      <div class="window-controls">
        <button class="wc-btn minimize" @click="window.api.minimizeWindow()" />
        <button class="wc-btn maximize" @click="window.api.toggleMaximize()" />
        <button class="wc-btn close" @click="window.api.closeWindow()" />
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
  position: relative;
  user-select: none;
}

.drag-region {
  position: absolute;
  inset: 0;
  -webkit-app-region: drag;
  z-index: 0;
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 1;
  -webkit-app-region: no-drag;
}

.app-name {
  font-weight: 600;
  color: var(--color-accent);
}

.sidebar-toggle,
.icon-btn {
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
  line-height: 1;
}
.sidebar-toggle:hover,
.icon-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

.version { margin-right: 4px; }

/* macOS-style traffic lights */
.window-controls {
  display: flex;
  gap: 6px;
  margin-left: 8px;
}
.wc-btn {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  transition: opacity var(--transition-fast);
}
.wc-btn:hover { opacity: 0.8; }
.wc-btn.minimize { background: #f59e0b; }
.wc-btn.maximize { background: #22c55e; }
.wc-btn.close    { background: #ef4444; }
</style>
