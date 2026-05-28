import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/news',
      name: 'news',
      component: () => import('@/views/NewsView.vue'),
    },
    {
      path: '/kb',
      name: 'kb',
      component: () => import('@/views/KnowledgeBaseView.vue'),
    },
  ],
})

export default router
