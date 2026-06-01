import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/pages/HomeView.vue'),
    },
    {
      path: '/news',
      name: 'news',
      component: () => import('@/pages/NewsView.vue'),
    },
    {
      path: '/kb/:kbId',
      name: 'kb-detail',
      component: () => import('@/pages/KnowledgeBaseView.vue'),
      props: true,
    },
  ],
})

export default router
