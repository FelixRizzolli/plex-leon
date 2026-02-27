import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// ─── Route definitions ────────────────────────────────────────────────────────
// Using hash history so Electron file:// URIs resolve correctly

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@views/HomeView.vue'),
    meta: { title: 'Home' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior: (_to, _from, savedPosition) =>
    savedPosition ?? { top: 0 },
})

// Update document title on each navigation
router.afterEach((to) => {
  const title = to.meta.title as string | undefined
  document.title = title ? `plex-leon · ${title}` : 'plex-leon'
})

export default router
