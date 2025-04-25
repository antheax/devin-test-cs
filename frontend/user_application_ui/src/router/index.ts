import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import UserManagement from '../views/UserManagement.vue'
import ApplicationRecords from '../views/ApplicationRecords.vue'
import TenantManagement from '../views/TenantManagement.vue'

declare global {
  interface ImportMeta {
    env: Record<string, string>
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/users',
      name: 'users',
      component: UserManagement
    },
    {
      path: '/applications',
      name: 'applications',
      component: ApplicationRecords
    },
    {
      path: '/tenants',
      name: 'tenants',
      component: TenantManagement
    }
  ]
})

export default router
