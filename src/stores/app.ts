import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

import type { AppInfo, AsyncStatus } from '@/types';

// ─── App-level store – version info, theme, global state ─────────────────────

export const useAppStore = defineStore('app', () => {
  // ── State ────────────────────────────────────────────────────────────────
  const appInfo = ref<AppInfo | null>(null);
  const theme = ref<'dark' | 'light'>('dark');
  const sidebarCollapsed = ref(false);
  const initStatus = ref<AsyncStatus>('idle');

  // ── Getters ──────────────────────────────────────────────────────────────
  const isDark = computed(() => theme.value === 'dark');
  const isReady = computed(() => initStatus.value === 'success');

  // ── Actions ──────────────────────────────────────────────────────────────
  async function init(): Promise<void> {
    if (initStatus.value !== 'idle') return;
    initStatus.value = 'loading';
    try {
      const [name, version] = await Promise.all([
        window.api.getAppName(),
        window.api.getAppVersion(),
      ]);
      appInfo.value = { name, version };
      initStatus.value = 'success';
    } catch (err) {
      console.error('App init failed', err);
      initStatus.value = 'error';
      // Provide fallback so the UI always renders
      appInfo.value = { name: 'plex-leon', version: '0.0.0' };
    }
  }

  function toggleTheme(): void {
    theme.value = theme.value === 'dark' ? 'light' : 'dark';
    document.documentElement.classList.toggle('dark', theme.value === 'dark');
  }

  function toggleSidebar(): void {
    sidebarCollapsed.value = !sidebarCollapsed.value;
  }

  return {
    appInfo,
    theme,
    sidebarCollapsed,
    initStatus,
    isDark,
    isReady,
    init,
    toggleTheme,
    toggleSidebar,
  };
});
