import type { RouteRecordRaw } from 'vue-router';

import { createRouter, createWebHashHistory } from 'vue-router';

// ─── Route definitions ────────────────────────────────────────────────────────
// Using hash history so Electron file:// URIs resolve correctly

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'dashboard',
    component: () => import('@views/DashboardView.vue'),
    meta: { title: 'Dashboard' },
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@views/SettingsView.vue'),
    meta: { title: 'Settings' },
  },
  {
    path: '/help',
    name: 'help',
    component: () => import('@views/HelpView.vue'),
    meta: { title: 'Help' },
  },
  {
    path: '/utility/prepare',
    name: 'utility-prepare',
    component: () => import('@views/UtilityPrepareView.vue'),
    meta: { title: 'Utility: Prepare' },
  },
  {
    path: '/utility/episode-check',
    name: 'utility-episode-check',
    component: () => import('@views/UtilityEpisodeCheckView.vue'),
    meta: { title: 'Utility: Episode Check' },
  },
  {
    path: '/utility/migrate',
    name: 'utility-migrate',
    component: () => import('@views/UtilityMigrateView.vue'),
    meta: { title: 'Utility: Migrate' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    redirect: '/',
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior: (_to, _from, savedPosition) => savedPosition ?? { top: 0 },
});

// Update document title on each navigation
router.afterEach((to) => {
  const title = to.meta.title as string | undefined;
  document.title = title ? `plex-leon · ${title}` : 'plex-leon';
});

export default router;
