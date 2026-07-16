<!-- src/components/PostBoard.vue -->
<template>
  <div class="board-container">
    <!-- 상단 검색 및 글쓰기 바 -->
    <div class="filter-bar">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input v-model="searchQuery" @input="handleSearch" type="text" placeholder="검색어를 입력하세요..." class="search-input" />
      </div>
      <button @click="openWriteModal" class="write-top-btn">✏️ 글쓰기</button>
    </div>

    <!-- 좌우 분할 레이아웃 -->
    <div class="board-layout">
      
      <!-- ⬅️ 왼쪽 사이드바: 모바일에서는 가로로 넘겨보는 상단 영역으로 변환 -->
      <aside class="sidebar-ranking">
        <!-- 1. 조회수 높은 인기 게시글 -->
        <div class="ranking-card">
          <h4 class="ranking-title">🔥 실시간 인기글</h4>
          <ul v-if="topViewedPosts.length > 0" class="ranking-list">
            <li v-for="(post, index) in topViewedPosts" :key="'view-'+post.id" @click="toggleDetailFromRanking(post.id)" class="ranking-item">
              <span class="rank-number">{{ index + 1 }}</span>
              <span class="rank-post-title">{{ post.title }}</span>
              <span class="rank-stat">👁️ {{ post.views }}</span>
            </li>
          </ul>
          <div v-else class="no-ranking">집계된 데이터가 없습니다.</div>
        </div>

        <!-- 2. 좋아요 많은 추천 게시글 -->
        <div class="ranking-card">
          <h4 class="ranking-title">❤️ 추천 게시글</h4>
          <ul v-if="topLikedPosts.length > 0" class="ranking-list">
            <li v-for="(post, index) in topLikedPosts" :key="'like-'+post.id" @click="toggleDetailFromRanking(post.id)" class="ranking-item">
              <span class="rank-number highlight">{{ index + 1 }}</span>
              <span class="rank-post-title">{{ post.title }}</span>
              <span class="rank-stat font-like">❤️ {{ post.likes }}</span>
            </li>
          </ul>
          <div v-else class="no-ranking">집계된 데이터가 없습니다.</div>
        </div>

        <!-- 3. 구미 플레이스 브랜드 홍보 광고 배너 -->
        <div class="promo-banner">
          <div class="promo-badge">AD</div>
          <div class="promo-content">
            <span class="promo-emoji">
              <img :src="logoImg" alt="어디갈구미 로고" class="promo-logo-image" />
            </span>
            <h5 class="promo-title">구미 플레이스</h5>
            <p class="promo-desc">내 취향에 딱 맞는 핫플레이스와 숨은 맛집을 AI 챗봇과 함께 찾아보세요!</p>
            <button @click="triggerPromoAction" class="promo-btn">지금 찾으러 가기 🚀</button>
          </div>
        </div>
      </aside>

      <!-- ➡️ 오른쪽 영역: 전체 게시글 목록 -->
      <main class="main-post-area">
        <div class="post-list">
          <div v-if="paginatedPosts.length === 0" class="no-posts">등록된 게시글이 없습니다.</div>
          
          <div v-for="post in paginatedPosts" :key="post.id" class="post-card" :class="{ 'is-active': activePostId === post.id }">
            <!-- 상단 요약 -->
            <div class="post-summary-row" @click="toggleDetail(post.id)">
              <div class="post-main-info">
                <h3 class="post-title">{{ post.title }}</h3>
                <div class="post-meta">
                  <span class="author">👤 {{ post.author }}</span>
                  <span class="divider">|</span>
                  <span>📅 {{ post.date }}</span>
                </div>
              </div>
              <div class="post-stats">
                <span>👁️ {{ post.views }}</span>
                <span @click.stop="handleLike(post.id)" class="like-stat-btn">
                  ❤️ {{ post.likes }}
                </span>
              </div>
            </div>

            <!-- 펼쳐지는 상세 영역 -->
            <div v-if="activePostId === post.id" class="post-detail-content">
              <p class="full-text">{{ post.summary }}</p>
              <div class="detail-actions">
                <button @click="openEditModal(post)" class="action-btn edit">✍️ 수정</button>
                <button @click="handleDelete(post.id)" class="action-btn delete">🗑️ 삭제</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 페이지네이션 UI -->
        <div v-if="totalPages > 1" class="pagination-container">
          <button :disabled="currentPage === 1" @click="currentPage--" class="page-btn prev">이전</button>
          <button v-for="page in totalPages" :key="page" @click="currentPage = page" :class="['page-number-btn', { active: currentPage === page }]">
            {{ page }}
          </button>
          <button :disabled="currentPage === totalPages" @click="currentPage++" class="page-btn next">다음</button>
        </div>
      </main>
    </div>

    <!-- [모달] 글쓰기 및 수정 통합 팝업 -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content">
        <h3>{{ isEditMode ? '게시글 수정' : '새 게시글 작성' }}</h3>
        <input v-model="form.author" type="text" placeholder="작성자명" class="modal-input" />
        <input v-model="form.title" type="text" placeholder="제목을 입력하세요" class="modal-input" />
        <textarea v-model="form.summary" placeholder="내용을 입력하세요" class="modal-textarea"></textarea>
        <input v-model="form.password" type="password" placeholder="비밀번호를 입력하세요 (수정/삭제용)" class="modal-input" />
        
        <div class="modal-buttons">
          <button @click="submitForm" class="btn-primary">저장</button>
          <button @click="showModal = false" class="btn-secondary">취소</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineEmits } from 'vue'
import axios from 'axios'
import logoImg from '../assets/logo.svg' // App.vue와 같은 depth의 assets 폴더에서 로고 가져오기

const API_URL = 'https://gumi-information.onrender.com/api/posts'

// 부모 컴포넌트로 챗봇 열기 이벤트를 보내기 위한 설정
const emit = defineEmits(['open-chatbot'])

const searchQuery = ref('')
const posts = ref([])
const activePostId = ref(null)

// 페이지네이션
const currentPage = ref(1)
const itemsPerPage = 8

// 모달 및 폼 관리
const showModal = ref(false)
const isEditMode = ref(false)
const currentPostId = ref(null)
const form = ref({ title: '', summary: '', author: '', password: '' })

// 조회수 상위 5개 추출
const topViewedPosts = computed(() => {
  return [...posts.value]
    .sort((a, b) => b.views - a.views)
    .slice(0, 5)
})

// 좋아요 상위 5개 추출
const topLikedPosts = computed(() => {
  return [...posts.value]
    .sort((a, b) => b.likes - a.likes)
    .slice(0, 5)
})

// 페이징된 목록
const paginatedPosts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return posts.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(posts.value.length / itemsPerPage))
})

// 목록 조회
const fetchPosts = async () => {
  try {
    const response = await axios.get(API_URL, { params: { search: searchQuery.value } })
    posts.value = response.data
  } catch (error) {
    console.error(error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchPosts()
}

// 상세조회 (토글 및 조회수 증가)
const toggleDetail = async (id) => {
  if (activePostId.value === id) {
    activePostId.value = null
  } else {
    try {
      const response = await axios.get(`${API_URL}/${id}`)
      activePostId.value = id
      
      const target = posts.value.find(p => p.id === id)
      if (target) target.views = response.data.views
    } catch (error) {
      alert('게시글을 불러오지 못했습니다.')
    }
  }
}

// 왼쪽 사이드바 랭킹 클릭 시 본문의 해당 상세글 열어주기 & 해당 페이지로 강제 이동
const toggleDetailFromRanking = async (id) => {
  const targetIndex = posts.value.findIndex(p => p.id === id)
  if (targetIndex !== -1) {
    currentPage.value = Math.floor(targetIndex / itemsPerPage) + 1
    await toggleDetail(id)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// 광고 클릭 액션 핸들러
const triggerPromoAction = () => {
  emit('open-chatbot')
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 작성 모달 열기
const openWriteModal = () => {
  isEditMode.value = false
  form.value = { title: '', summary: '', author: '익명', password: '' }
  showModal.value = true
}

// 수정 모달 열기
const openEditModal = (post) => {
  isEditMode.value = true
  currentPostId.value = post.id
  form.value = { title: post.title, summary: post.summary, author: post.author, password: '' }
  showModal.value = true
}

// 작성 & 수정 전송
const submitForm = async () => {
  if (!form.value.title || !form.value.summary || !form.value.password) {
    alert('비밀번호를 포함한 모든 빈칸을 채워주세요.')
    return
  }

  if (isEditMode.value) {
    try {
      await axios.put(`${API_URL}/${currentPostId.value}`, form.value)
      alert('수정 완료되었습니다.')
      showModal.value = false
      fetchPosts()
    } catch (error) {
      if (error.response?.status === 403) alert('비밀번호가 틀렸습니다.')
      else alert('수정에 실패했습니다.')
    }
  } else {
    const today = new Date()
    const formattedDate = `${today.getFullYear()}.${String(today.getMonth() + 1).padStart(2, '0')}.${String(today.getDate()).padStart(2, '0')}`
    
    try {
      await axios.post(API_URL, { ...form.value, date: formattedDate })
      alert('등록 완료되었습니다.')
      showModal.value = false
      currentPage.value = 1
      fetchPosts()
    } catch (error) {
      alert('등록 실패')
    }
  }
}

// 삭제
const handleDelete = async (id) => {
  const password = prompt('게시글을 삭제하려면 비밀번호를 입력하세요:')
  if (!password) return

  try {
    await axios.delete(`${API_URL}/${id}`, { params: { password } })
    alert('삭제되었습니다.')
    activePostId.value = null
    
    const tempTotalPages = Math.ceil((posts.value.length - 1) / itemsPerPage)
    if (currentPage.value > tempTotalPages && currentPage.value > 1) {
      currentPage.value = tempTotalPages
    }
    
    fetchPosts()
  } catch (error) {
    if (error.response?.status === 403) alert('비밀번호가 일치하지 않습니다.')
    else alert('삭제 실패')
  }
}

// 좋아요
const handleLike = async (id) => {
  try {
    const response = await axios.post(`${API_URL}/${id}/like`)
    const target = posts.value.find(p => p.id === id)
    if (target) {
      target.likes = response.data.likes
    }
  } catch (error) {
    console.error('좋아요 반영 실패:', error)
  }
}

onMounted(() => { fetchPosts() })
</script>

<style scoped>
/* ==========================================
   1. 기본 레이아웃 구성 및 공통 스타일 (박싱 리셋)
   ========================================== */
*, *::before, *::after {
  box-sizing: border-box;
}

.board-container {
  max-width: 1040px;
  margin: 0 auto;
  padding: 0 4px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  width: 100%;
}

.filter-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  width: 100%;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 0;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #aaa;
  font-size: 13px;
}

.search-input {
  width: 100%;
  padding: 10px 10px 10px 34px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  background: #f8f9fa;
  transition: all 0.2s ease;
}

.search-input:focus {
  background: #fff;
  border-color: #7c5cfc;
}

.write-top-btn {
  padding: 0 14px;
  background: #7c5cfc;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: bold;
  cursor: pointer;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.write-top-btn:hover {
  background: #6a48e8;
}

.board-layout {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

/* ==========================================
   2. 모바일 특화 사이드바 가로 스크롤 레이아웃
   ========================================== */
.sidebar-ranking {
  display: flex;
  flex-direction: row;
  overflow-x: auto;
  overflow-y: hidden; /* 세로 스크롤 방지 */
  gap: 12px;
  width: 100%;
  padding: 4px 4px 12px 4px; /* 스크롤 터치 마진 확보 */
  scrollbar-width: none; /* Firefox */
  -webkit-overflow-scrolling: touch; /* iOS 가속 스크롤 */
}

.sidebar-ranking::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

/* 가로 슬라이더 형태 카드 크기 설정 */
.ranking-card, .promo-banner {
  flex: 0 0 280px; /* 줄어들지도 않고(0), 늘어나지도 않고(0), 너비 280px 유지 */
  max-width: 280px;
  background: #fff;
  border: 1px solid #e1e4e6;
  border-radius: 12px;
  padding: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
  display: block; /* 가로 배열 내 렌더링 유지 보장 */
}

.ranking-title {
  margin: 0 0 10px 0;
  font-size: 13px;
  font-weight: 800;
  color: #111;
  border-bottom: 1.5px solid #eaeaea;
  padding-bottom: 6px;
  text-align: left;
}

.ranking-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  cursor: pointer;
  padding: 2px 0;
  transition: opacity 0.2s;
}

.ranking-item:hover {
  opacity: 0.7;
}

.rank-number {
  font-weight: bold;
  color: #7c5cfc;
  width: 14px;
  text-align: center;
}

.rank-number.highlight {
  color: #e03131;
}

.rank-post-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #333;
  text-align: left;
}

.rank-stat {
  font-size: 10px;
  color: #888;
  white-space: nowrap;
}

.font-like {
  color: #e03131;
  font-weight: 500;
}

.no-ranking {
  font-size: 11px;
  color: #bbb;
  text-align: center;
  padding: 20px 0;
}

/* 홍보 광고 배너 스타일 */
.promo-banner {
  position: relative;
  background: linear-gradient(135deg, #3d2b7a 0%, #1a1030 100%);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 12px rgba(76, 39, 137, 0.25);
}

.promo-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.8);
  font-size: 8px;
  font-weight: bold;
  padding: 1px 4px;
  border-radius: 3px;
  text-transform: uppercase;
}

.promo-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.promo-emoji {
  margin-bottom: 4px;
}

.promo-logo-image {
  height: 38px;
  width: auto;
  object-fit: contain;
  vertical-align: middle;
}

.promo-title {
  font-size: 14px;
  font-weight: 800;
  margin: 4px 0 2px 0;
  color: #ffffff;
}

.promo-desc {
  font-size: 10.5px;
  line-height: 1.4;
  color: #dddddd;
  margin: 0 0 10px 0;
  word-break: keep-all;
}

.promo-btn {
  width: 100%;
  padding: 8px;
  border: none;
  border-radius: 6px;
  background: #ffffff;
  color: #6a48e8;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

/* ==========================================
   3. 우측 게시판 본문 영역
   ========================================== */
.main-post-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.post-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.post-card {
  border: 1px solid #e1e4e6;
  border-radius: 12px;
  background: #fff;
  overflow: hidden;
  transition: box-shadow 0.2s;
  width: 100%;
}

.post-card.is-active {
  border-color: #7c5cfc;
}

.post-summary-row {
  padding: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  gap: 8px;
}

.post-main-info {
  flex: 1;
  min-width: 0;
  text-align: left;
}

.post-title {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 700;
  color: #222;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.post-meta {
  font-size: 11.5px;
  color: #888;
}

.divider {
  margin: 0 4px;
  color: #eee;
}

.post-stats {
  display: flex;
  gap: 8px;
  font-size: 11.5px;
  color: #666;
  flex-shrink: 0;
}

.like-stat-btn {
  cursor: pointer;
  user-select: none;
}

.post-detail-content {
  padding: 16px;
  background: #fafafa;
  border-top: 1px solid #f1f3f5;
  text-align: left;
}

.full-text {
  font-size: 13px;
  color: #333;
  line-height: 1.5;
  margin: 0 0 12px 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.detail-actions {
  display: flex;
  gap: 6px;
  justify-content: flex-end;
}

.action-btn {
  padding: 4px 10px;
  border: 1px solid #ddd;
  background: #fff;
  border-radius: 6px;
  font-size: 11px;
  cursor: pointer;
}

.action-btn.delete {
  color: #e03131;
  border-color: #ffc9c9;
}

.no-posts {
  text-align: center;
  color: #aaa;
  padding: 40px 0;
  font-size: 13px;
}

/* 페이지네이션 */
.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  margin-top: 20px;
  padding-top: 14px;
  border-top: 1px solid #f1f3f5;
}

.page-btn {
  padding: 5px 10px;
  border: 1px solid #dee2e6;
  background-color: #ffffff;
  border-radius: 6px;
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
}

.page-btn:disabled {
  color: #adb5bd;
  background-color: #e9ecef;
  cursor: not-allowed;
}

.page-number-btn {
  width: 28px;
  height: 28px;
  border: 1px solid #dee2e6;
  background-color: #ffffff;
  border-radius: 6px;
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-number-btn.active {
  background-color: #7c5cfc;
  color: #ffffff;
  border-color: #7c5cfc;
}

/* 모달 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.modal-content {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.15);
  text-align: left;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 12px;
  font-size: 15px;
}

.modal-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
  margin-bottom: 8px;
  font-size: 13px;
  outline: none;
}

.modal-textarea {
  width: 100%;
  height: 80px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
  margin-bottom: 10px;
  font-size: 13px;
  resize: none;
  outline: none;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
}

.btn-primary {
  background: #7c5cfc;
  color: #fff;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  font-size: 12px;
}

.btn-secondary {
  background: #eee;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

/* ==========================================
   4. 데스크톱 반응형 뷰 (768px 이상)
   ========================================== */
@media (min-width: 768px) {
  .board-container {
    padding: 0;
  }

  .filter-bar {
    gap: 12px;
    margin-bottom: 24px;
  }

  .search-icon {
    left: 14px;
    font-size: 15px;
  }

  .search-input {
    padding: 12px 12px 12px 40px;
    font-size: 14px;
  }

  .write-top-btn {
    padding: 0 20px;
    font-size: 14px;
  }

  /* 데스크톱은 다시 사이드바와 본문 그리드로 격자 배치 */
  .board-layout {
    display: grid;
    grid-template-columns: 280px 1fr;
    gap: 24px;
  }

  .sidebar-ranking {
    flex-direction: column;
    overflow-x: visible;
    gap: 20px;
    padding: 0;
  }

  .ranking-card, .promo-banner {
    flex: none;
    width: 100%;
    max-width: 100%;
    padding: 18px;
  }

  .ranking-title {
    font-size: 14px;
    margin-bottom: 14px;
    padding-bottom: 8px;
  }

  .ranking-item {
    font-size: 13px;
  }

  .rank-stat {
    font-size: 11px;
  }

  .promo-logo-image {
    height: 55px;
  }

  .promo-title {
    font-size: 16px;
    margin-bottom: 6px;
  }

  .promo-desc {
    font-size: 11.5px;
    line-height: 1.5;
    margin-bottom: 14px;
  }

  .promo-btn {
    padding: 10px;
    font-size: 12px;
  }

  .post-summary-row {
    padding: 18px;
  }

  .post-title {
    font-size: 16px;
  }

  .post-meta {
    font-size: 13px;
  }

  .post-stats {
    font-size: 13px;
  }

  .post-detail-content {
    padding: 20px;
  }

  .full-text {
    font-size: 14px;
  }

  .action-btn {
    padding: 6px 12px;
    font-size: 12px;
  }

  .pagination-container {
    gap: 6px;
  }

  .page-btn {
    padding: 6px 12px;
    font-size: 13px;
  }

  .page-number-btn {
    width: 32px;
    height: 32px;
    font-size: 13px;
  }
}
</style>