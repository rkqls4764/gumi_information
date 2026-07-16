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
      
      <!-- ⬅️ 왼쪽 사이드바: 실시간 랭킹 및 브랜드 홍보 광고 -->
      <aside class="sidebar-ranking">
        <!-- 1. 조회수 높은 인기 게시글 -->
        <div class="ranking-card">
          <h4 class="ranking-title">🔥 실시간 인기글 (조회순)</h4>
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
          <h4 class="ranking-title">❤️ 추천 게시글 (좋아요순)</h4>
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
            <p class="promo-desc">내 취향에 딱 맞는 구미의 핫플레이스와 숨은 맛집을 스마트한 AI 챗봇과 함께 찾아보세요!</p>
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
    <div v-if="showModal" class="modal-overlay">
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

const API_URL = 'http://localhost:8000/api/posts'

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
  return Math.ceil(posts.value.length / itemsPerPage)
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
  // 부모(App.vue)에게 챗봇창을 활성화해달라는 신호를 전달합니다.
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
/* 전체 레이아웃을 여유있게 변경 */
.board-container { max-width: 1040px; margin: 0 auto; padding: 20px; font-family: sans-serif; }
.filter-bar { display: flex; gap: 12px; margin-bottom: 24px; }
.search-box { position: relative; flex: 1; }
.search-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: #aaa; }
.search-input { width: 100%; box-sizing: border-box; padding: 12px 12px 12px 40px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
.write-top-btn { padding: 0 20px; background: #111; color: #fff; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }

/* 좌측 사이드바와 우측 본문 배치를 위한 그리드 레이아웃 */
.board-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
  align-items: start;
}

/* 사이드바 영역 */
.sidebar-ranking {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.ranking-card {
  background: #fff;
  border: 1px solid #e1e4e6;
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}
.ranking-title {
  margin: 0 0 14px 0;
  font-size: 14px;
  font-weight: 800;
  color: #111;
  border-bottom: 1.5px solid #eaeaea;
  padding-bottom: 8px;
}
.ranking-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.ranking-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  cursor: pointer;
  padding: 4px 0;
  transition: opacity 0.2s;
}
.ranking-item:hover {
  opacity: 0.7;
}
.rank-number {
  font-weight: bold;
  color: #1a73e8;
  width: 16px;
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
}
.rank-stat {
  font-size: 11px;
  color: #888;
  white-space: nowrap;
}
.font-like {
  color: #e03131;
  font-weight: 500;
}
.no-ranking {
  font-size: 12px;
  color: #bbb;
  text-align: center;
  padding: 12px 0;
}

/* 홍보 광고 배너 스타일 */
/* 배너 내부 로고 이미지 크기 및 비율 최적화 */
.promo-logo-image {
  height: 55px;        /* 배너 텍스트 높이와 어울리는 크기 (필요시 조정 가능) */
  width: auto;         /* 가로 세로 비율 강제 유지 */
  object-fit: contain;
  vertical-align: middle;
}
.promo-banner {
  position: relative;
  background: linear-gradient(135deg, #111111 0%, #2c3e50 100%);
  color: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.promo-badge {
  position: absolute;
  top: 10px;
  right: 12px;
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.8);
  font-size: 9px;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.promo-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.promo-emoji {
  font-size: 28px;
  margin-bottom: 8px;
}
.promo-title {
  font-size: 16px;
  font-weight: 800;
  margin: 0 0 6px 0;
  letter-spacing: -0.3px;
  color: #ffffff;
}
.promo-desc {
  font-size: 11.5px;
  line-height: 1.5;
  color: #dddddd;
  margin: 0 0 14px 0;
  word-break: keep-all;
}
.promo-btn {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 8px;
  background: #ffffff;
  color: #111111;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}
.promo-btn:hover {
  background: #f1f3f5;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(255, 255, 255, 0.15);
}
.promo-btn:active {
  transform: translateY(0);
}

/* 우측 게시판 본문 영역 */
.main-post-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.post-list { display: flex; flex-direction: column; gap: 12px; }
.post-card { border: 1px solid #e1e4e6; border-radius: 12px; background: #fff; overflow: hidden; transition: box-shadow 0.2s; }
.post-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.post-card.is-active { border-color: #495057; }

.post-summary-row { padding: 18px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
.post-title { margin: 0 0 6px 0; font-size: 16px; font-weight: 700; color: #222; }
.post-meta { font-size: 13px; color: #888; }
.divider { margin: 0 6px; color: #eee; }
.post-stats { display: flex; gap: 12px; font-size: 13px; color: #666; }
.like-stat-btn {
  cursor: pointer;
  transition: transform 0.1s ease;
  user-select: none;
}
.like-stat-btn:hover {
  transform: scale(1.15);
}

.post-detail-content { padding: 20px; background: #fafafa; border-top: 1px solid #f1f3f5; }
.full-text { font-size: 14px; color: #333; line-height: 1.6; margin: 0 0 16px 0; white-space: pre-wrap; }
.detail-actions { display: flex; gap: 8px; justify-content: flex-end; }
.action-btn { padding: 6px 12px; border: 1px solid #ddd; background: #fff; border-radius: 6px; font-size: 12px; cursor: pointer; }
.action-btn.delete { color: #e03131; border-color: #ffc9c9; }

.no-posts { text-align: center; color: #aaa; padding: 40px 0; }

/* 페이지네이션 */
.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  margin-top: 28px;
  padding-top: 16px;
  border-top: 1px solid #f1f3f5;
}
.page-btn {
  padding: 6px 12px;
  border: 1px solid #dee2e6;
  background-color: #ffffff;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.page-btn:hover:not(:disabled) {
  background-color: #f1f3f5;
}
.page-btn:disabled {
  color: #adb5bd;
  background-color: #e9ecef;
  cursor: not-allowed;
}
.page-number-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #dee2e6;
  background-color: #ffffff;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.page-number-btn:hover {
  background-color: #f1f3f5;
}
.page-number-btn.active {
  background-color: #111111;
  color: #ffffff;
  border-color: #111111;
}

/* 모달 */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: #fff; padding: 24px; border-radius: 12px; width: 90%; max-width: 460px; box-shadow: 0 8px 20px rgba(0,0,0,0.15); }
.modal-content h3 { margin-top: 0; margin-bottom: 16px; }
.modal-input { width: 100%; box-sizing: border-box; padding: 10px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 10px; font-size: 14px; }
.modal-textarea { width: 100%; box-sizing: border-box; height: 100px; padding: 10px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 14px; font-size: 14px; resize: none; }
.modal-buttons { display: flex; justify-content: flex-end; gap: 8px; }
.btn-primary { background: #111; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; }
.btn-secondary { background: #eee; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; }

/* 📱 모바일/좁은 화면 반응형 분할 해제 */
@media (max-width: 768px) {
  .board-layout {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}
</style>