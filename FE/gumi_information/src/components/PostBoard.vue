<!-- src/components/PostBoard.vue -->
<template>
  <div class="board-container">
    <!-- 검색 바 -->
    <div class="filter-bar">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input v-model="searchQuery" @input="handleSearch" type="text" placeholder="검색어를 입력하세요..." class="search-input" />
      </div>
      <button @click="openWriteModal" class="write-top-btn">✏️ 글쓰기</button>
    </div>

    <!-- 게시글 목록 -->
    <div class="post-list">
      <div v-if="paginatedPosts.length === 0" class="no-posts">등록된 게시글이 없습니다.</div>
      
      <!-- posts 대신 paginatedPosts를 순회하도록 변경 -->
      <div v-for="post in paginatedPosts" :key="post.id" class="post-card" :class="{ 'is-active': activePostId === post.id }">
        <!-- 상단 요약 (클릭 시 상세 열기 + 조회수 증가) -->
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

        <!-- 펼쳐지는 상세 영역 (상세조회 및 수정/삭제 기능) -->
        <div v-if="activePostId === post.id" class="post-detail-content">
          <p class="full-text">{{ post.summary }}</p>
          <div class="detail-actions">
            <button @click="openEditModal(post)" class="action-btn edit">✍️ 수정</button>
            <button @click="handleDelete(post.id)" class="action-btn delete">🗑️ 삭제</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 🎯 [신규 추가] 페이지네이션 UI -->
    <div v-if="totalPages > 1" class="pagination-container">
      <button 
        :disabled="currentPage === 1" 
        @click="currentPage--" 
        class="page-btn prev"
      >
        이전
      </button>
      
      <button 
        v-for="page in totalPages" 
        :key="page" 
        @click="currentPage = page"
        :class="['page-number-btn', { active: currentPage === page }]"
      >
        {{ page }}
      </button>

      <button 
        :disabled="currentPage === totalPages" 
        @click="currentPage++" 
        class="page-btn next"
      >
        다음
      </button>
    </div>

    <!-- [모달] 글쓰기 및 수정 통합 팝업 -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <h3>{{ isEditMode ? '게시글 수정' : '새 게시글 작성' }}</h3>
        <input v-model="form.author" type="text" placeholder="작성자명" class="modal-input" />
        <input v-model="form.title" type="text" placeholder="제목을 입력하세요" class="modal-input" />
        <textarea v-model="form.summary" placeholder="내용을 입력하세요" class="modal-textarea"></textarea>
        <!-- 권한 검증용 암호 필드 -->
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
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const API_URL = 'http://localhost:8000/api/posts'

const searchQuery = ref('')
const posts = ref([])
const activePostId = ref(null) // 현재 펼쳐진 상세글 ID

// 🎯 [신규 추가] 페이지네이션 상태 변수
const currentPage = ref(1)
const itemsPerPage = 10

// 모달 및 폼 상태 관리
const showModal = ref(false)
const isEditMode = ref(false)
const currentPostId = ref(null)
const form = ref({ title: '', summary: '', author: '', password: '' })

// 🎯 [신규 추가] 현재 페이지에 해당하는 10개의 게시글만 가공하는 계산 프로퍼티
const paginatedPosts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return posts.value.slice(start, end)
})

// 🎯 [신규 추가] 총 페이지 수 계산 프로퍼티
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

// 🎯 [신규 추가] 검색어 입력 시 첫 페이지로 리셋하며 목록 조회
const handleSearch = () => {
  currentPage.value = 1
  fetchPosts()
}

// 상세조회 (토글 방식 및 조회수 실시간 증가 반영)
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

// 작성 & 수정 전송 통합 처리
const submitForm = async () => {
  if (!form.value.title || !form.value.summary || !form.value.password) {
    alert('비밀번호를 포함한 모든 빈칸을 채워주세요.')
    return
  }

  if (isEditMode.value) {
    // 수정 요청 (PUT)
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
    // 작성 요청 (POST)
    const today = new Date()
    const formattedDate = `${today.getFullYear()}.${String(today.getMonth() + 1).padStart(2, '0')}.${String(today.getDate()).padStart(2, '0')}`
    
    try {
      await axios.post(API_URL, { ...form.value, date: formattedDate })
      alert('등록 완료되었습니다.')
      showModal.value = false
      currentPage.value = 1 // 새 글 등록 시 첫 페이지로 이동
      fetchPosts()
    } catch (error) {
      alert('등록 실패')
    }
  }
}

// 삭제 요청 처리 (DELETE)
const handleDelete = async (id) => {
  const password = prompt('게시글을 삭제하려면 비밀번호를 입력하세요:')
  if (!password) return

  try {
    await axios.delete(`${API_URL}/${id}`, { params: { password } })
    alert('삭제되었습니다.')
    activePostId.value = null
    
    // 만약 현재 페이지의 마지막 글을 삭제했다면 이전 페이지로 이동시킴
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

// 좋아요 증가 API 호출 함수
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
.board-container { max-width: 800px; margin: 0 auto; padding: 20px; font-family: sans-serif; }
.filter-bar { display: flex; gap: 12px; margin-bottom: 20px; }
.search-box { position: relative; flex: 1; }
.search-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: #aaa; }
.search-input { width: 100%; box-sizing: border-box; padding: 12px 12px 12px 40px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
.write-top-btn { padding: 0 20px; background: #111; color: #fff; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }

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

/* 🎯 [신규 추가] 페이지네이션 스타일 */
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

/* 모달 컴포넌트 스타일 */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: #fff; padding: 24px; border-radius: 12px; width: 90%; max-width: 460px; box-shadow: 0 8px 20px rgba(0,0,0,0.15); }
.modal-content h3 { margin-top: 0; margin-bottom: 16px; }
.modal-input { width: 100%; box-sizing: border-box; padding: 10px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 10px; font-size: 14px; }
.modal-textarea { width: 100%; box-sizing: border-box; height: 100px; padding: 10px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 14px; font-size: 14px; resize: none; }
.modal-buttons { display: flex; justify-content: flex-end; gap: 8px; }
.btn-primary { background: #111; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; }
.btn-secondary { background: #eee; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
</style>