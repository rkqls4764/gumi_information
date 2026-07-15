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
          <!-- 💡 [수정] CategorySelector 컴포넌트에 @submit 이벤트 리스너를 연동합니다 -->
          <CategorySelector @submit="handleCategorySelection" />
        </section>
        <section class="right-section">
          <PostBoard />
        </section>
      </template>

      <!-- [2] 💡 캘린더 탭 -->
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
          <PostBoard />
        </section>
      </template>

    </main>

    <!-- 🤖 [챗봇 레이어] 모든 페이지 공통 적용 -->
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

        <!-- 🤖 [추가] 카테고리 셀렉터 칩 영역 -->
        <div class="chat-category-bar">
          <span class="category-bar-title">관심사 필터:</span>
          <div class="category-chips">
            <button 
              v-for="cat in chatCategories" 
              :key="cat.value"
              :class="['category-chip', { active: selectedChatCategory === cat.value }]"
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

      <!-- 플로팅 고정 버튼 -->
      <button class="chatbot-toggle-btn" @click="isChatOpen = !isChatOpen" :class="{ open: isChatOpen }">
        <span v-if="!isChatOpen">💬 챗봇 문의</span>
        <span v-else>✕ 닫기</span>
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, nextTick, computed } from 'vue'
import CategorySelector from './components/CategorySelector.vue'
import PostBoard from './components/PostBoard.vue'
import LocalInfoView from './views/LocalInfoView.vue'
import MapView from './views/MapView.vue'

// 탭 메뉴 설정
const currentMenu = ref('home')

const menus = [
  { id: 'home', name: '홈', icon: '🏠' },
  { id: 'local-info', name: '캘린더', icon: '📅' },
  { id: 'map', name: '지도', icon: '📍' },
  { id: 'community', name: '커뮤니티', icon: '💬' }
]

// 🤖 챗봇 상태 및 로직 변수들 선언
const isChatOpen = ref(false)
const userMessage = ref('')
const isBotLoading = ref(false)
const messageContainer = ref(null) // DOM 엘리먼트 참조용 ref

// 🤖 [추가] 챗봇용 카테고리 상태 정의
const selectedChatCategory = ref(null) // 기본값은 필터링 없음(null)
const chatCategories = [
  { label: '운동', value: '운동', icon: '💪' },
  { label: '음식', value: '음식', icon: '🍕' },
  { label: '여행', value: '여행', icon: '✈️' },
  { label: '쇼핑', value: '쇼핑', icon: '🛍️' }
]

// 입력창 플레이스홀더 동적 변경
const getInputPlaceholder = computed(() => {
  if (selectedChatCategory.value) {
    return `[${selectedChatCategory.value}] 관련 질문을 입력하세요...`
  }
  return "메시지를 입력하세요..."
})

// 💡 [추가 및 수정] 메인 화면 CategorySelector 완료 이벤트를 가로채 처리하는 함수
const handleCategorySelection = (categoryTitle) => {
  // 1. 전달받은 카테고리 값으로 필터 적용
  selectedChatCategory.value = categoryTitle
  
  // 2. 챗봇 창 열기
  isChatOpen.value = true
  
  // 3. 챗봇 가이드 메시지 누적
  chatMessages.value.push({ 
    sender: 'bot', 
    text: `🎯 메인 화면에서 [${categoryTitle}] 카테고리를 설정하셨습니다! 이제 질문창에 찾으시는 내용을 입력하면 관련된 정보를 맞춤 추천해 드려요.` 
  })
  
  scrollToBottom()
}

// 카테고리 필터 토글 함수
const toggleCategory = (categoryValue) => {
  if (selectedChatCategory.value === categoryValue) {
    selectedChatCategory.value = null // 다시 누르면 필터 해제
    chatMessages.value.push({ 
      sender: 'bot', 
      text: '카테고리 필터링이 해제되었습니다. 전체 데이터에서 정보를 찾습니다.' 
    })
  } else {
    selectedChatCategory.value = categoryValue
    chatMessages.value.push({ 
      sender: 'bot', 
      text: `🔔 [${categoryValue}] 카테고리가 지정되었습니다. 이제 질문하시면 데이터베이스의 ${categoryValue} 관련 정보를 바탕으로 추천을 드립니다.` 
    })
  }
  scrollToBottom()
}

// 기본 웰컴 메시지 설정
const chatMessages = ref([
  { sender: 'bot', text: '안녕하세요! LocalHub 가이드 챗봇입니다. 구미/경북 지역에 대해 궁금한 점이 있으신가요?' }
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
    // 🤖 FastAPI 서버로 질문과 현재 선택된 카테고리를 함께 전송
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: inputMessage,
        category: selectedChatCategory.value // 선택된 카테고리 정보 ("음식", "운동" 등 또는 null)
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    
    // 백엔드가 반환한 {"reply": "..."} 값을 화면에 출력
    chatMessages.value.push({ sender: 'bot', text: data.reply })
    
  } catch (error) {
    console.error('API 통신 에러 발생:', error)
    chatMessages.value.push({ 
      sender: 'bot', 
      text: '죄송합니다. 시스템에 일시적인 오류가 발생하여 답변을 생성하지 못했습니다.' 
    })
  } finally {
    isBotLoading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
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
  width: 380px;
  height: 520px;
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

/* 🤖 챗봇 내부 상단 카테고리 바 스타일 */
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
  background-color: #111111;
  border-color: #111111;
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
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

.chat-input-form button:disabled {
  background-color: #868e96;
  cursor: not-allowed;
}

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
  
  .chatbot-window {
    width: calc(100vw - 32px);
    height: 440px;
  }
}
</style>