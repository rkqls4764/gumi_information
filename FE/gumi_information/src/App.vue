<!-- src/App.vue -->
<template>
  <div class="localhub-container">
    <!-- 상단 네비게이션 -->
    <header class="localhub-header">
      <div class="header-content">
        <!-- 로고 -->
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
      
      <!-- [1] 홈 탭 -->
      <template v-if="currentMenu === 'home'">
        <section class="left-section">
          <CategorySelector />
        </section>
        <section class="right-section">
          <PostBoard />
        </section>
      </template>

      <!-- [2] 지역 정보 탭 -->
      <template v-else-if="currentMenu === 'info'">
        <section class="full-section">
          <LocalInfoView /> 
        </section>
      </template>

      <!-- [3] 지도 탭 -->
      <template v-else-if="currentMenu === 'map'">
        <section class="full-section">
          <div class="section-header">
            <h2>📍 내 주변 지도 검색</h2>
            <p>구미/경북 지역의 핵심 스팟과 관광지를 한눈에 지도로 보여줍니다.</p>
          </div>
          <div class="map-placeholder">
            <span style="font-size: 40px; margin-bottom: 12px;">🗺️</span>
            <p>지도 API가 연동될 영역입니다.</p>
          </div>
        </section>
      </template>

      <!-- [4] 커뮤니티 탭 -->
      <template v-else-if="currentMenu === 'community'">
        <section class="full-section">
          <div class="section-header">
            <h2>💬 자유 소통 공간</h2>
            <p>이웃 주민들과 편하게 이야기와 추천 명소 정보를 나누는 게시판입니다.</p>
          </div>
          <PostBoard />
        </section>
      </template>

    </main>

    <!-- 🤖 [신규 수정한 챗봇 레이어] 모든 페이지 공통 적용 -->
    <div class="chatbot-wrapper">
      <!-- 챗봇 창 (isChatOpen이 true일 때만 표시) -->
      <div v-if="isChatOpen" class="chatbot-window">
        <div class="chat-header">
          <div class="chat-bot-profile">
            <span class="bot-avatar">🤖</span>
            <div>
              <h4>LocalHub 챗봇</h4>
              <span class="online-dot">● 온라인</span>
            </div>
          </div>
          <button class="chat-close-btn" @click="isChatOpen = false">✕</button>
        </div>
        
        <!-- 대화 메세지 영역 -->
        <div class="chat-messages" ref="messageContainer">
          <div v-for="(msg, idx) in chatMessages" :key="idx" :class="['message-bubble', msg.sender]">
            <p>{{ msg.text }}</p>
          </div>
        </div>

        <!-- 메세지 입력창 -->
        <form @submit.prevent="sendMessage" class="chat-input-form">
          <input 
            v-model="userMessage" 
            type="text" 
            placeholder="메세지를 입력하세요..." 
            required 
          />
          <button type="submit">전송</button>
        </form>
      </div>

      <!-- 플로팅 고정 버튼 -->
      <button class="chatbot-toggle-btn" @click="isChatOpen = !isChatOpen" :class="{ open: isChatOpen }">
        <span v-if="!isChatOpen">💬 챗봇 문의</span>
        <span v-else>✕ 닫기</span>
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import CategorySelector from './components/CategorySelector.vue'
import PostBoard from './components/PostBoard.vue'
import LocalInfoView from './views/LocalInfoView.vue'

const currentMenu = ref('home')

const menus = [
  { id: 'home', name: '홈', icon: '🏠' },
  { id: 'info', name: '지역 정보', icon: '🗺️' },
  { id: 'map', name: '지도', icon: '📍' },
  { id: 'community', name: '커뮤니티', icon: '💬' }
]

// 🤖 챗봇 상태 및 로직 변수들
const isChatOpen = ref(false)
const userMessage = ref('')
const messageContainer = ref(null)
const chatMessages = ref([
  { sender: 'bot', text: '안녕하세요! 구미/경북 로컬 허브 도우미봇입니다. 무엇을 도와드릴까요? ✨' }
])

// 스크롤 아래로 내리는 헬퍼 함수
const scrollToBottom = async () => {
  await nextTick()
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}

// 사용자 메시지 전송 및 자동 앵무새 답변(테스트용)
const sendMessage = () => {
  if (!userMessage.value.trim()) return

  // 1. 유저 메세지 푸시
  chatMessages.value.push({ sender: 'user', text: userMessage.value })
  const savedMsg = userMessage.value
  userMessage.value = ''
  scrollToBottom()

  // 2. 0.8초 후 로봇 자동 답변 (추후 백엔드나 AI 연동 시 이 부분을 수정)
  setTimeout(() => {
    chatMessages.value.push({ 
      sender: 'bot', 
      text: `📢 "${savedMsg}"라고 말씀하셨군요! 현재 AI 챗봇 기능을 고도화 중입니다. 조금만 기다려 주세요!` 
    })
    scrollToBottom()
  }, 800)
}
</script>

<style scoped>
/* (질문자님의 기존 CSS 스타일은 그대로 유지되며, 하단에 챗봇 스타일만 안전하게 추가되었습니다) */
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
  border-bottom: 3px solid #111;
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

/* 🤖 [신규] 플로팅 챗봇 버튼 & 창 전용 디자인 */
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
  background-color: #111111;
  color: #ffffff;
  border: none;
  padding: 14px 22px;
  border-radius: 30px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease-in-out;
  display: flex;
  align-items: center;
  gap: 6px;
}

.chatbot-toggle-btn:hover {
  transform: translateY(-2px);
  background-color: #222222;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.chatbot-toggle-btn.open {
  background-color: #fa5252;
}

.chatbot-window {
  width: 360px;
  height: 480px;
  background-color: #ffffff;
  border-radius: 16px;
  border: 1px solid #e9ecef;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
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
  background-color: #111111;
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
  font-size: 16px;
  cursor: pointer;
  opacity: 0.7;
}
.chat-close-btn:hover { opacity: 1; }

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
  background-color: #111111;
  color: #ffffff;
  align-self: flex-end;
  border-top-right-radius: 2px;
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
.chat-input-form input:focus { border-color: #111; }

.chat-input-form button {
  background-color: #111;
  color: white;
  border: none;
  padding: 0 16px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
}

/* 📱 모바일 및 태블릿 대응 미디어 쿼리 */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
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
  .logo-text { font-size: 20px; }
  .logo-sub { display: none; }
  .nav-item { padding: 0 12px; font-size: 14px; }
  .menu-name { display: none; }
  .menu-icon { font-size: 22px; }
  
  /* 모바일에서는 챗봇 크기 조정 */
  .chatbot-window {
    width: calc(100vw - 32px);
    height: 400px;
  }
}
</style>