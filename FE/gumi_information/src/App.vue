<template>
  <div class="localhub-container">
    <!-- 상단 네비게이션 -->
    <header class="localhub-header">
      <div class="header-content">
        <!-- 로고 (클릭 시 홈으로 이동) -->
        <div class="logo-area" @click="currentMenu = 'home'" style="cursor: pointer;">
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
      
      <!-- [1] 홈 탭: 좌측(관심선택) + 우측(게시판) 그리드 레이아웃 그대로 유지 -->
      <template v-if="currentMenu === 'home'">
        <!-- 좌측: 관심 분야 선택 -->
        <section class="left-section">
          <CategorySelector />
        </section>

        <!-- 우측: 검색 및 게시글 리스트 -->
        <section class="right-section">
          <PostBoard />
        </section>
      </template>

      <!-- [2] 지역 정보 탭: 정보 화면 -->
      <template v-else-if="currentMenu === 'info'">
        <section class="full-section">
          <div class="section-header">
            <h2>🗺️ 맞춤형 지역 정보</h2>
            <p>취향 선택에 따른 유용한 소식과 핫플레이스를 모아보세요.</p>
          </div>
          <!-- 지역 정보용 컴포넌트가 따로 있다면 이 자리에 넣어주세요 -->
          <LocalInfoView />
        </section>
      </template>

      <!-- [3] 지도 탭: 지도 화면 -->
      <template v-else-if="currentMenu === 'map'">
        <section class="full-section">
          <div class="section-header">
            <h2>📍 내 주변 지도 검색</h2>
            <p>구미/경북 지역의 핵심 스팟과 관광지를 한눈에 지도로 보여줍니다.</p>
          </div>
          <!-- 임시 지도 플레이스홀더 영역 -->
          <div class="map-placeholder">
            <span style="font-size: 40px; margin-bottom: 12px;">🗺️</span>
            <p>지도 API가 연동될 영역입니다.</p>
          </div>
        </section>
      </template>

      <!-- [4] 커뮤니티 탭: 커뮤니티 전용 화면 -->
      <template v-else-if="currentMenu === 'community'">
        <section class="full-section">
          <div class="section-header">
            <h2>💬 자유 소통 공간</h2>
            <p>이웃 주민들과 편하게 이야기와 추천 명소 정보를 나누는 게시판입니다.</p>
          </div>
          <!-- 기존 컴포넌트인 게시판을 화면 전체 크기로 출력 -->
          <PostBoard />
        </section>
      </template>

    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import CategorySelector from './components/CategorySelector.vue'
import PostBoard from './components/PostBoard.vue'

// 👈 기존의 LocalInfoTest 대신 새로 작성한 LocalInfoView를 연결합니다!
import LocalInfoView from './views/LocalInfoView.vue' // 폴더 위치에 맞게 경로 지정 (views 혹은 components)

// 기본 선택 메뉴는 'home' (홈 화면)
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

/* 단일 전체 화면 렌더링 시 그리드를 풀고 1줄로 변경 */
.main-content:has(.full-section) {
  display: block;
}

.left-section, .right-section, .full-section {
  background-color: #ffffff;
  border: 1px solid #e9ecef;
  border-radius: 16px; /* 둥근 테두리 더 넓게 */
  padding: 32px; /* 패딩 확장 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* 탭 타이틀 영역 스타일 */
.section-header {
  margin-bottom: 24px;
  border-bottom: 1.5px solid #f1f3f5;
  padding-bottom: 16px;
}
.section-header h2 {
  font-size: 22px;
  font-weight: 800;
  margin: 0 0 8px 0;
}
.section-header p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 임시 지도 영역 */
.map-placeholder {
  width: 100%;
  height: 500px;
  background-color: #f1f3f5;
  border-radius: 12px;
  border: 1.5px dashed #dee2e6;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #868e96;
}

/* 📱 모바일 및 태블릿 대응 미디어 쿼리 */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr; /* 세로로 쌓이도록 변경 */
    gap: 24px;
    padding: 16px;
  }
  .left-section, .right-section, .full-section {
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