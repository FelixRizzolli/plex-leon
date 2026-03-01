import type { RouteRecordRaw } from 'vue-router';

import { createRouter, createWebHashHistory } from 'vue-router';
import { i18n } from '../i18n';

// ─── Route definitions ────────────────────────────────────────────────────────
// Using hash history so Electron file:// URIs resolve correctly

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'dashboard',
    component: () => import('@views/DashboardView.vue'),
    meta: { titleKey: 'dashboard.title' },
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@views/SettingsView.vue'),
    meta: { titleKey: 'settings.title' },
  },
  {
    path: '/help',
    name: 'help',
    component: () => import('@views/HelpView.vue'),
    meta: { titleKey: 'help.title' },
  },
  {
    path: '/utility/prepare',
    name: 'utility-prepare',
    component: () => import('@views/UtilityPrepareView.vue'),
    meta: { titleKey: ['utility.title', 'utility.prepare.title'] },
  },
  {
    path: '/utility/episode-check',
    name: 'utility-episode-check',
    component: () => import('@views/UtilityEpisodeCheckView.vue'),
    meta: { titleKey: ['utility.title', 'utility.episode-check.title'] },
  },
  {
    path: '/utility/migrate',
    name: 'utility-migrate',
    component: () => import('@views/UtilityMigrateView.vue'),
    meta: { titleKey: ['utility.title', 'utility.migrate.title'] },
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
  const titleKey = to.meta.titleKey as string | string[] | undefined;
  if (!titleKey) {
    document.title = 'plex-leon';
    return;
  }

  const resolveTitle = (key: string) => i18n.global.t(key) as string;
  let title = '';
  if (Array.isArray(titleKey)) title = titleKey.map(resolveTitle).join(': ');
  else title = resolveTitle(titleKey);

  document.title = title ? `plex-leon · ${title}` : 'plex-leon';
});

export default router;
