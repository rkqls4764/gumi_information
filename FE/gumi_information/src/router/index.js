import { createRouter, createWebHistory } from 'vue-router'

// 각 화면 컴포넌트 불러오기
import LocalInfoView from '../views/LocalInfoView.vue'
import MapView from '../views/MapView.vue'
import CommunityView from '../views/CommunityView.vue'

const routes = [
  {
    path: '/',
    redirect: '/local-info' // 첫 접속 시 '지역 정보'로 리다이렉트
  },
  {
    path: '/local-info',
    name: 'LocalInfo',
    component: LocalInfoView
  },
  {
    path: '/map',
    name: 'Map',
    component: MapView
  },
  {
    path: '/community',
    name: 'Community',
    component: CommunityView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router