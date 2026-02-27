<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@stores/app'
import type { NavItem } from '@/types'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const navItems: NavItem[] = [
  { label: 'Home',     icon: '🏠', route: '/' },
  { label: 'Settings', icon: '⚙️', route: '/settings' },
]

function navigate(item: NavItem): void {
  router.push(item.route)
}
</script>

<template>
  <Transition name="slide">
    <nav v-show="!appStore.sidebarCollapsed" class="app-sidebar">
      <ul class="nav-list">
        <li
          v-for="item in navItems"
          :key="item.route"
          class="nav-item"
          :class="{ active: route.path === item.route }"
          @click="navigate(item)"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </li>
      </ul>
    </nav>
  </Transition>
</template>

<style scoped>
.app-sidebar {
  width: var(--sidebar-width);
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  flex-shrink: 0;
}

.nav-list {
  list-style: none;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--color-text-muted);
  transition: background var(--transition-fast), color var(--transition-fast);
  user-select: none;
}
.nav-item:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}
.nav-item.active {
  background: var(--color-accent-subtle);
  color: var(--color-accent);
  font-weight: 600;
}

.nav-icon { font-size: 16px; }
.nav-label { font-size: 13px; }

/* Slide transition for collapse */
.slide-enter-active, .slide-leave-active {
  transition: width var(--transition-base), opacity var(--transition-base);
  overflow: hidden;
}
.slide-enter-from, .slide-leave-to {
  width: 0 !important;
  opacity: 0;
}
</style>
