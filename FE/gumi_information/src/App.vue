<template>
  <div class="localhub-container">
    <!-- 상단 네비게이션 -->
    <header class="localhub-header">
      <div class="header-content">
        <!-- 로고 -->
        <div class="logo-area">
          <span class="logo-text">📍 LocalHub</span>
          <span class="logo-sub">구미/경북 지역 정보 & 커뮤니티</span>
        </div>
        
        <!-- 메뉴 -->
        <nav class="nav-menu">
          <button 
            v-for="menu in menus" 
            :key="menu.id"
            @click="currentMenu = menu.id"
            :class="['nav-item', { active: currentMenu === menu.id }]"
          >
            <span class="menu-icon">{{ menu.icon }}</span>
            <span class="menu-name">{{ menu.name }}</span>
          </button>
        </nav>
      </div>
    </header>

    <!-- 메인 컨텐츠 영역 -->
    <main class="main-content">
      <!-- 좌측: 관심 분야 선택 -->
      <section class="left-section">
        <CategorySelector />
      </section>

      <!-- 우측: 검색 및 게시글 리스트 -->
      <section class="right-section">
        <PostBoard />
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import CategorySelector from './components/CategorySelector.vue'
import PostBoard from './components/PostBoard.vue'

const currentMenu = ref('home')
const menus = [
  { id: 'home', name: '홈', icon: '🏠' },
  { id: 'info', name: '지역 정보', icon: '🗺️' },
  { id: 'map', name: '지도', icon: '📍' },
  { id: 'community', name: '커뮤니티', icon: '💬' }
]
</script>

<style scoped>
/* 전반적인 기본 폰트 크기 및 여백 키움 */
.localhub-container {
  min-height: 100vh;
  background-color: #f8f9fa;
  color: #212529;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.localhub-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: #ffffff;
  border-bottom: 1px solid #e9ecef;
}

.header-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 24px;
  height: 72px; /* 64px -> 72px로 확장 */
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-text {
  font-size: 24px; /* 더 크게 변경 */
  font-weight: 800;
  color: #111;
  letter-spacing: -0.5px;
}

.logo-sub {
  font-size: 13px;
  color: #868e96;
  border-left: 1.5px solid #dee2e6;
  padding-left: 12px;
}

.nav-menu {
  display: flex;
  height: 100%;
}

.nav-item {
  background: none;
  border: none;
  padding: 0 20px;
  height: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px; /* 14px -> 16px */
  font-weight: 600;
  color: #495057;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.2s ease-in-out;
}

.menu-icon {
  font-size: 18px;
}

.nav-item:hover {
  color: #111;
}

.nav-item.active {
  border-bottom: 3px solid #111;
  color: #111;
  font-weight: 800;
}

/* 메인 그리드 및 패딩 키움 */
.main-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 32px 24px;
  display: grid;
  grid-template-columns: 5fr 7fr;
  gap: 32px; /* 간격 확장 */
}

.left-section, .right-section {
  background-color: #ffffff;
  border: 1px solid #e9ecef;
  border-radius: 16px; /* 둥근 테두리 더 넓게 */
  padding: 32px; /* 패딩 확장 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* 📱 모바일 및 태블릿 대응 미디어 쿼리 */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr; /* 세로로 쌓이도록 변경 */
    gap: 24px;
    padding: 16px;
  }
  .left-section, .right-section {
    padding: 24px;
  }
}

@media (max-width: 640px) {
  .header-content {
    padding: 0 16px;
    height: 64px;
  }
  .logo-text {
    font-size: 20px;
  }
  .logo-sub {
    display: none; /* 모바일에서 서브 텍스트 숨김 */
  }
  .nav-item {
    padding: 0 12px;
    font-size: 14px;
  }
  .menu-name {
    display: none; /* 모바일에서 텍스트 감추고 아이콘만 노출 */
  }
  .menu-icon {
    font-size: 22px;
  }
}
</style>