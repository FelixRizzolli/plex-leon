import type { RouteRecordRaw } from 'vue-router';

import { useI18n } from 'vue-i18n';
import { createRouter, createWebHashHistory } from 'vue-router';
const { t } = useI18n();

// ─── Route definitions ────────────────────────────────────────────────────────
// Using hash history so Electron file:// URIs resolve correctly

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'dashboard',
    component: () => import('@views/DashboardView.vue'),
    meta: { title: t('dashboard.title') },
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@views/SettingsView.vue'),
    meta: { title: t('settings.title') },
  },
  {
    path: '/help',
    name: 'help',
    component: () => import('@views/HelpView.vue'),
    meta: { title: t('help.title') },
  },
  {
    path: '/utility/prepare',
    name: 'utility-prepare',
    component: () => import('@views/UtilityPrepareView.vue'),
    meta: { title: `${t('utility.title')}: ${t('utility.prepare.title')}` },
  },
  {
    path: '/utility/episode-check',
    name: 'utility-episode-check',
    component: () => import('@views/UtilityEpisodeCheckView.vue'),
    meta: { title: `${t('utility.title')}: ${t('utility.episode-check.title')}` },
  },
  {
    path: '/utility/migrate',
    name: 'utility-migrate',
    component: () => import('@views/UtilityMigrateView.vue'),
    meta: { title: `${t('utility.title')}: ${t('utility.migrate.title')}` },
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
