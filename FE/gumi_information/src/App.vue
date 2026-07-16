<!-- src/App.vue -->
<template>
  <div class="localhub-container" :class="{ 'bottom-nav-active': isMobile }">
    <!-- 상단 네비게이션 (데스크톱 전용 / 모바일에서는 로고만 상단 표시) -->
    <header class="localhub-header">
      <div class="header-content">
        <!-- 로고 -->
        <div class="logo-area" @click="currentMenu = 'home'" style="cursor: pointer;">
          <span class="logo-text">
            <img :src="logoImg" alt="구미 플레이스 로고" class="logo-image" />
            어디갈구미?
          </span>
          <span class="logo-sub">구미/경북 지역 정보 & 커뮤니티</span>
        </div>
        
        <!-- 데스크톱 전용 메뉴 (CSS로 모바일에서 숨김 처리) -->
        <nav class="nav-menu desktop-only">
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
      
      <!-- [1] 홈 탭 -->
      <template v-if="currentMenu === 'home'">
        <section class="left-section">
          <CategorySelector
            @category-selected="selectedCategory = $event"
          />
        </section>
        <section class="right-section">
          <PlaceRecommendation
            :category="selectedCategory"
          />
        </section>
      </template>

      <!-- [2] 캘린더 탭 -->
      <template v-else-if="currentMenu === 'local-info'">
        <section class="full-section">
          <LocalInfoView />
        </section>
      </template>

      <!-- [3] 지도 탭 -->
      <template v-else-if="currentMenu === 'map'">
        <section class="full-section">
          <MapView />
        </section>
      </template>

      <!-- [4] 커뮤니티 탭 -->
      <template v-else-if="currentMenu === 'community'">
        <section class="full-section">
          <div class="section-header">
            <h2>💬 자유 소통 공간</h2>
            <p>이웃 주민들과 편하게 이야기와 추천 명소 정보를 나누는 게시판입니다.</p>
          </div>
          <PostBoard @open-chatbot="isChatOpen = true" />
        </section>
      </template>

    </main>

    <!-- 📱 모바일 전용 하단 네비게이션 바 -->
    <nav class="mobile-bottom-nav mobile-only">
      <button 
        v-for="menu in menus" 
        :key="menu.id"
        @click="currentMenu = menu.id"
        :class="['mobile-nav-item', { active: currentMenu === menu.id }]"
      >
        <span class="mobile-menu-icon">{{ menu.icon }}</span>
        <span class="mobile-menu-name">{{ menu.name }}</span>
      </button>
    </nav>

    <!-- 🤖 [챗봇 레이어] 모든 페이지 공통 적용 -->
    <div class="chatbot-wrapper" :class="{ 'is-open': isChatOpen }">
      <!-- 챗봇 창 (isChatOpen이 true일 때만 표시) -->
      <div v-if="isChatOpen" class="chatbot-window">
        <div class="chat-header">
          <div class="chat-bot-profile">
            <span class="bot-avatar">🍇</span>
            <div>
              <h4>마이구 가이드</h4>
              <span class="online-dot">● 온라인 (탱글)</span>
            </div>
          </div>
          <button class="chat-close-btn" @click="isChatOpen = false">✕</button>
        </div>

        <!-- 카테고리 셀렉터 칩 영역 -->
        <div class="chat-category-bar">
          <span class="category-bar-title">관심사를 선택해 정확한 장소를 추천 받으세요!</span>
          <div class="category-chips">
            <button 
              v-for="cat in chatCategories" 
              :key="cat.value"
              :disabled="isBotLoading"
              :class="[
                'category-chip', 
                { 
                  active: selectedChatCategory === cat.value,
                  disabled: isBotLoading
                }
              ]"
              @click="toggleCategory(cat.value)"
            >
              {{ cat.icon }} {{ cat.label }}
            </button>
          </div>
        </div>
        
        <!-- 대화 메세지 영역 -->
        <div class="chat-messages" ref="messageContainer">
          <div v-for="(msg, idx) in chatMessages" :key="idx" :class="['message-bubble', msg.sender]">
            <p>{{ msg.text }}</p>
          </div>

          <!-- 대답을 기다리는 동안 노출되는 로딩 요소 -->
          <div v-if="isBotLoading" class="gumi-loading-wrap">
            <div class="gumi-loader-container">
              <div class="orbit-item landmark-mountain">⛰️</div>
              <div class="orbit-item landmark-river">🌊</div>
              <div class="orbit-item landmark-building">⛩️</div>
              <div class="orbit-item landmark-factory">🏭</div>
              
              <div class="gumi-jelly-pin">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="70" height="70">
                  <defs>
                    <radialGradient id="jellyPinGrad" cx="35%" cy="30%" r="70%">
                      <stop offset="0%" stop-color="#D8B4FE" />
                      <stop offset="50%" stop-color="#9333EA" />
                      <stop offset="100%" stop-color="#581C87" />
                    </radialGradient>
                    <linearGradient id="leafGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stop-color="#A7F3D0" />
                      <stop offset="100%" stop-color="#059669" />
                    </linearGradient>
                  </defs>
                  <ellipse cx="50" cy="92" rx="20" ry="4" fill="#E9DDF2" opacity="0.8" />
                  <path d="M50 15 C30 15 15 30 15 50 C15 75 50 92 50 92 C50 92 85 75 85 50 C85 30 70 15 50 15 Z" fill="url(#jellyPinGrad)"/>
                  <circle cx="50" cy="40" r="12" fill="#C084FC" opacity="0.9" />
                  <circle cx="41" cy="48" r="9" fill="#A855F7" opacity="0.9" />
                  <circle cx="59" cy="48" r="9" fill="#A855F7" opacity="0.9" />
                  <circle cx="50" cy="56" r="10" fill="#7E22CE" opacity="0.9" />
                  <path d="M43 18 C38 8 48 8 50 16 C52 8 62 8 57 18 Z" fill="url(#leafGrad)" />
                  <path d="M28 35 A 18 18 0 0 1 42 22" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" fill="none" opacity="0.6" />
                  <polygon points="62,35 64,30 69,28 64,26 62,21 60,26 55,28 60,30" fill="#FFFFFF" />
                </svg>
              </div>
            </div>
            <div class="gumi-status-text">마이구가 핫플을 골라내고 있어요...</div>
          </div>
        </div>

        <!-- 메세지 입력창 -->
        <form @submit.prevent="sendMessage" class="chat-input-form">
          <input 
            v-model="userMessage" 
            type="text" 
            :placeholder="getInputPlaceholder" 
            required 
          />
          <button type="submit" :disabled="isBotLoading">전송</button>
        </form>
      </div>

      <!-- 플로팅 고정 버튼 (챗봇이 닫혀있거나 PC일 때만 활성화) -->
      <button 
        v-show="!isChatOpen" 
        class="chatbot-toggle-btn" 
        @click="isChatOpen = !isChatOpen"
      >
        <span>🍇 마이구 챗봇</span>
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, nextTick, computed, onMounted, onUnmounted } from 'vue'
import logoImg from './assets/logo.png' 
import CategorySelector from './components/CategorySelector.vue'
import PostBoard from './components/PostBoard.vue'
import LocalInfoView from './views/LocalInfoView.vue'
import MapView from './views/MapView.vue'
import PlaceRecommendation from './components/PlaceRecommendation.vue'

const selectedCategory = ref(null)
const currentMenu = ref('home')

const menus = [
  { id: 'home', name: '홈', icon: '🏠' },
  { id: 'local-info', name: '캘린더', icon: '📅' },
  { id: 'map', name: '지도', icon: '📍' },
  { id: 'community', name: '커뮤니티', icon: '💬' }
]

// 화면 해상도 체크 (모바일 여부 확인)
const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 640
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

// 🤖 챗봇 상태 및 로직 변수들 선언
const isChatOpen = ref(false)
const userMessage = ref('')
const isBotLoading = ref(false)
const messageContainer = ref(null) 

// 🤖 챗봇용 카테고리 상태 정의
const selectedChatCategory = ref(null) 
const chatCategories = [
  { label: '운동', value: '운동', icon: '💪' },
  { label: '음식', value: '음식', icon: '🍕' },
  { label: '여행', value: '여행', icon: '✈️' },
  { label: '쇼핑', value: '쇼핑', icon: '🛍️' }
]

// 입력창 플레이스홀더 동적 변경
const getInputPlaceholder = computed(() => {
  if (selectedChatCategory.value) {
    return `[${selectedChatCategory.value}] 질문을 입력하라구...`
  }
  return "메시지를 입력하라구..."
})

// 메인 화면 CategorySelector 완료 이벤트를 가로채 처리하는 함수
const handleCategorySelection = (categoryTitle) => {
  selectedChatCategory.value = categoryTitle
  isChatOpen.value = true
  
  chatMessages.value.push({ 
    sender: 'bot', 
    text: `🎯 메인 화면에서 [${categoryTitle}] 카테고리를 선택했다구! 나에게 질문창에 필요한 정보를 입력하면 찰떡 정보를 맞춤 추천해 줄게.` 
  })
  
  scrollToBottom()
}

// 카테고리 필터 토글 함수
const toggleCategory = (categoryValue) => {
  if (selectedChatCategory.value === categoryValue) {
    selectedChatCategory.value = null 
    chatMessages.value.push({ 
      sender: 'bot', 
      text: '카테고리 필터링이 해제되었습니다. 전체 구미 데이터에서 정보를 찾습니다.' 
    })
  } else {
    selectedChatCategory.value = categoryValue
    chatMessages.value.push({ 
      sender: 'bot', 
      text: `🔔 [${categoryValue}] 카테고리가 지정되었습니다. 이제 질문하시면 내가 ${categoryValue} 핫플을 골라줄구미!` 
    })
  }
  scrollToBottom()
}

// 기본 웰컴 메시지 설정
const chatMessages = ref([
  { sender: 'bot', text: '안녕! 나는 구미 지역 지키미 젤리 요정 "마이구"야. 구미/경북의 볼거리와 맛집에 대해 내게 편하게 물어봐 보라구! 🍇' }
])

// 스크롤 아래로 내리는 함수
const scrollToBottom = async () => {
  await nextTick()
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}

// 챗봇 메시지 전송 로직
const sendMessage = async () => {
  if (!userMessage.value.trim() || isBotLoading.value) return

  const inputMessage = userMessage.value
  chatMessages.value.push({ sender: 'user', text: inputMessage })
  userMessage.value = ''
  
  isBotLoading.value = true
  scrollToBottom()

  try {
    const response = await fetch('https://gumi-information.onrender.com/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: inputMessage,
        category: selectedChatCategory.value
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    chatMessages.value.push({ sender: 'bot', text: data.reply })
    
  } catch (error) {
    console.error('API 통신 에러 발생:', error)
    chatMessages.value.push({ 
      sender: 'bot', 
      text: '미안해구미... 일시적인 오류가 나서 정보를 찾지 못했어. 조금만 이따가 다시 물어봐줘!' 
    })
  } finally {
    isBotLoading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
/* 반응형 전용 유틸리티 */
.desktop-only {
  display: flex;
}
.mobile-only {
  display: none !important;
}

/* 로고 텍스트 전체 영역 정렬 */
.logo-text {
  display: flex;
  align-items: center;
  gap: 8px; 
  font-size: 24px; 
  font-weight: 800;
  color: #111;
  margin: 0;
}

/* 로고 이미지 크기 및 비율 조절 */
.logo-image {
  height: 40px;      
  width: auto;        
  object-fit: contain;
  display: inline-block;
  vertical-align: middle;
}

.localhub-container {
  min-height: 100vh;
  background-color: #f8f9fa;
  color: #212529;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  transition: padding-bottom 0.2s ease;
}

/* 모바일 하단바 활성화 시 패딩 추가 */
.localhub-container.bottom-nav-active {
  padding-bottom: 64px;
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
  height: 72px;
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
  font-size: 24px;
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
  font-size: 16px;
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
  border-bottom: 3px solid #7c5cfc;
  color: #111;
  font-weight: 800;
}
.main-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 32px 24px;
  display: grid;
  grid-template-columns: 5fr 7fr;
  gap: 32px;
}
.main-content:has(.full-section) {
  display: block;
}
.left-section, .right-section, .full-section {
  background-color: #ffffff;
  border: 1px solid #e9ecef;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
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

/* 🤖 플로팅 챗봇 버튼 & 창 전용 디자인 */
.chatbot-wrapper {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 999;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 16px;
}

.chatbot-toggle-btn {
  background-color: #701a75; 
  color: #ffffff;
  border: none;
  padding: 14px 22px;
  border-radius: 30px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(112, 26, 117, 0.2);
  transition: all 0.2s ease-in-out;
  display: flex;
  align-items: center;
  gap: 6px;
}

.chatbot-toggle-btn:hover {
  transform: translateY(-2px);
  background-color: #4a044e;
  box-shadow: 0 6px 20px rgba(112, 26, 117, 0.3);
}

.chatbot-window {
  width: 450px;
  height: 650px;
  background-color: #ffffff;
  border-radius: 16px;
  border: 1px solid #e9ecef;
  box-shadow: 0 8px 32px rgba(112, 26, 117, 0.12);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.25s ease-out;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.chat-header {
  background-color: #701a75; 
  color: #ffffff;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-bot-profile {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bot-avatar {
  font-size: 24px;
}

.chat-header h4 {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
}

.online-dot {
  font-size: 11px;
  color: #40c057;
  font-weight: bold;
}

.chat-close-btn {
  background: none;
  border: none;
  color: #ffffff;
  font-size: 18px;
  cursor: pointer;
  opacity: 0.8;
  padding: 4px;
}
.chat-close-btn:hover { opacity: 1; }

.chat-category-bar {
  background-color: #f1f3f5;
  padding: 10px 14px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.category-bar-title {
  font-size: 11px;
  font-weight: 700;
  color: #495057;
}

.category-chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.category-chip {
  background-color: #ffffff;
  border: 1px solid #dee2e6;
  border-radius: 20px;
  padding: 5px 10px;
  font-size: 12px;
  font-weight: 600;
  color: #495057;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
}

.category-chip:hover {
  background-color: #f8f9fa;
  border-color: #ced4da;
}

.category-chip.active {
  background-color: #701a75; 
  border-color: #701a75;
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(112, 26, 117, 0.15);
}

.chat-messages {
  flex: 1;
  padding: 16px;
  background-color: #f8f9fa;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-bubble {
  margin: 0;
  white-space: pre-line;
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.4;
}

.message-bubble p { margin: 0; }

.message-bubble.bot {
  background-color: #ffffff;
  color: #212529;
  align-self: flex-start;
  border: 1px solid #e9ecef;
  border-top-left-radius: 2px;
}

.message-bubble.user {
  background-color: #701a75; 
  color: #ffffff;
  align-self: flex-end;
  border-top-right-radius: 2px;
}

/* AI 답변 생성 중 비활성화 스타일 */
.category-chip:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.chat-input-form {
  display: flex;
  padding: 12px;
  background-color: #ffffff;
  border-top: 1px solid #e9ecef;
  gap: 8px;
}

.chat-input-form input {
  flex: 1;
  border: 1px solid #ced4da;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
}
.chat-input-form input:focus { border-color: #701a75; }

.chat-input-form button {
  background-color: #701a75; 
  color: white;
  border: none;
  padding: 0 16px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
}

.chat-input-form button:disabled {
  background-color: #868e96;
  cursor: not-allowed;
}

/* 🍇 마이구 젤리 로딩 CSS */
.gumi-loading-wrap {
  align-self: flex-start;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 16px;
  padding: 12px 20px;
  box-shadow: 0 4px 12px rgba(112, 26, 117, 0.05);
  border-bottom-left-radius: 2px;
  animation: fadeIn 0.3s ease-out;
  border: 1px solid #E9DDF2;
  margin-top: 4px;
  margin-bottom: 4px;
}

.gumi-loader-container {
  position: relative;
  width: 120px;
  height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.gumi-jelly-pin {
  width: 70px;
  height: 70px;
  animation: jellyBounce 2s infinite ease-in-out;
  z-index: 2;
}

.orbit-item {
  position: absolute;
  font-size: 15px;
  animation: orbitRotate 3.5s infinite linear;
}

.landmark-mountain { animation-delay: 0s; }
.landmark-river    { animation-delay: -0.87s; }
.landmark-building { animation-delay: -1.75s; }
.landmark-factory  { animation-delay: -2.62s; }

.gumi-status-text {
  font-size: 11px;
  color: #701A75;
  font-weight: 600;
  margin-top: 4px;
  animation: textFlicker 1.5s infinite;
}

@keyframes jellyBounce {
  0%, 100% { transform: scale(1) translateY(0); }
  50% { transform: scaleY(1.08) scaleX(0.95) translateY(-8px); }
  75% { transform: scaleY(0.92) scaleX(1.04) translateY(1px); }
}

@keyframes orbitRotate {
  0% { transform: rotate(0deg) translate(45px) rotate(0deg) scale(1); opacity: 1; z-index: 3; }
  50% { transform: rotate(180deg) translate(45px) rotate(-180deg) scale(0.7); opacity: 0.4; z-index: 1; }
  100% { transform: rotate(360deg) translate(45px) rotate(-360deg) scale(1); opacity: 1; z-index: 3; }
}

@keyframes textFlicker {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 📱 반응형 분기 처리 (Tablet / Desktop Mid-range) */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
    gap: 24px;
    padding: 24px 16px;
  }
  .left-section, .right-section, .full-section {
    padding: 24px;
  }
}

/* 📱 모바일 최적화 (Mobile Phone, max-width: 640px) */
@media (max-width: 640px) {
  .desktop-only {
    display: none !important;
  }
  .mobile-only {
    display: flex !important;
  }

  /* 헤더 슬림화 및 로고 위주 노출 */
  .localhub-header {
    height: 56px;
    display: flex;
    align-items: center;
  }
  .header-content {
    padding: 0 16px;
    height: 100%;
    justify-content: center; /* 로고 중앙 정렬 */
  }
  .logo-text { 
    font-size: 18px; 
  }
  .logo-image {
    height: 32px;
  }
  .logo-sub { 
    display: none; 
  }

  /* 모바일 본문 영역 여백 최소화 */
  .main-content {
    padding: 16px 12px;
    gap: 16px;
  }
  .left-section, .right-section, .full-section {
    padding: 16px;
    border-radius: 12px;
  }

  /* 📱 모바일 전용 하단 앱바 네비게이션 스타일 */
  .mobile-bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 60px;
    background-color: #ffffff;
    border-top: 1px solid #e9ecef;
    display: flex;
    justify-content: space-around;
    align-items: center;
    z-index: 990;
    padding-bottom: env(safe-area-inset-bottom); /* iOS 노치 홈바 대응 */
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  }

  .mobile-nav-item {
    background: none;
    border: none;
    flex: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;
    color: #868e96;
    font-size: 11px;
    font-weight: 500;
    cursor: pointer;
  }

  .mobile-menu-icon {
    font-size: 20px;
  }

  .mobile-nav-item.active {
    color: #7c5cfc;
    font-weight: 700;
  }

  /* 📱 모바일 환경 챗봇 전체화면 오버레이 최적화 */
  .chatbot-wrapper {
    bottom: 0;
    right: 0;
    width: 100%;
    height: 0;
  }
  
  .chatbot-wrapper.is-open {
    height: 100%;
  }

  /* 챗봇 닫기 버튼을 모바일에 맞추어 우측 하단에 플로팅 배치 */
  .chatbot-toggle-btn {
    position: fixed;
    bottom: 76px; /* 하단 네비게이션과 겹치지 않는 위치 */
    right: 16px;
    padding: 12px 18px;
    font-size: 13px;
    border-radius: 24px;
    box-shadow: 0 4px 12px rgba(112, 26, 117, 0.3);
  }

  /* 챗봇 창 전체 화면 덮기 */
  .chatbot-window {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    height: -webkit-fill-available; /* 모바일 브라우저 주소창 높이 대응 */
    border-radius: 0;
    border: none;
    z-index: 1000;
    animation: slideUpMobile 0.25s ease-out;
  }

  @keyframes slideUpMobile {
    from { transform: translateY(100%); }
    to { transform: translateY(0); }
  }

  .chat-header {
    padding: 14px 16px;
  }
  
  .chat-close-btn {
    font-size: 22px; /* 터치하기 편하게 터치 타겟 크기 확대 */
    padding: 6px;
  }

  .chat-category-bar {
    padding: 8px 12px;
  }

  .category-chip {
    padding: 4px 8px;
    font-size: 11px;
  }

  .chat-messages {
    padding: 12px;
  }

  .message-bubble {
    font-size: 13px;
    max-width: 85%;
  }

  .chat-input-form {
    padding: 10px;
    padding-bottom: calc(10px + env(safe-area-inset-bottom)); /* iOS 노치 키보드 대응 */
  }

  .chat-input-form input {
    padding: 8px 12px;
    font-size: 13px;
  }

  .chat-input-form button {
    padding: 0 12px;
    font-size: 13px;
  }
}
</style>