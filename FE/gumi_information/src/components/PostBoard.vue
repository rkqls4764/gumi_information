<template>
  <div class="board-container">
    <!-- 검색 및 필터 바 -->
    <div class="filter-bar">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input 
          v-model="searchQuery"
          @input="fetchPosts" 
          type="text" 
          placeholder="검색어를 입력하세요 (제목, 내용)" 
          class="search-input"
        />
      </div>
      
      <div class="filter-actions">
        <select v-model="sortBy" class="sort-select">
          <option value="latest">최신순</option>
        </select>
        <button class="filter-btn">⚙️ 필터</button>
      </div>
    </div>

    <!-- 게시글 목록 -->
    <div class="post-list">
      <div v-if="posts.length === 0" class="no-posts">게시글이 없습니다. 첫 글을 작성해 보세요!</div>
      
      <div v-for="post in posts" :key="post.id" class="post-item">
        <!-- 이미지 플레이스홀더 -->
        <div class="post-thumbnail">🖼️</div>
        
        <!-- 게시글 정보 -->
        <div class="post-info">
          <div class="post-header">
            <h3 class="post-title">{{ post.title }}</h3>
            <span class="post-views">👁️ {{ post.views }}</span>
          </div>
          <p class="post-summary">{{ post.summary }}</p>
          
          <div class="post-footer">
            <div class="post-meta">
              <span class="author">{{ post.author }}</span>
              <span class="divider">|</span>
              <span>{{ post.date }}</span>
            </div>
            
            <div class="post-buttons">
              <button class="action-btn score">🤍 {{ post.likes }}</button>
              <button class="action-btn">🔖</button>
              <button class="action-btn">🔗</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 페이지네이션 & 글쓰기 -->
    <div class="board-footer">
      <div class="pagination">
        <button class="page-arrow">‹</button>
        <button class="page-num active">1</button>
        <button class="page-arrow">›</button>
      </div>

      <button @click="showWriteModal = true" class="write-btn">글쓰기</button>
    </div>

    <!-- 글쓰기 레이어 팝업 (모달) -->
    <div v-if="showWriteModal" class="modal-overlay">
      <div class="modal-content">
        <h3>새 게시글 작성</h3>
        <input v-model="newPost.author" type="text" placeholder="작성자명" class="modal-input" />
        <input v-model="newPost.title" type="text" placeholder="제목을 입력하세요" class="modal-input" />
        <textarea v-model="newPost.summary" placeholder="내용을 입력하세요" class="modal-textarea"></textarea>
        
        <div class="modal-buttons">
          <button @click="submitPost" class="btn-primary">등록</button>
          <button @click="showWriteModal = false" class="btn-secondary">취소</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API_URL = 'http://localhost:8000/api/posts' // FastAPI 서버 주소

const searchQuery = ref('')
const sortBy = ref('latest')
const posts = ref([])
const showWriteModal = ref(false)

// 새 게시글 폼 바인딩 변수
const newPost = ref({
  title: '',
  summary: '',
  author: '',
  date: ''
})

// 1. 게시글 목록 불러오기 (GET API 연동)
const fetchPosts = async () => {
  try {
    const response = await axios.get(API_URL, {
      params: { search: searchQuery.value }
    })
    posts.value = response.data
  } catch (error) {
    console.error('게시글 로드 실패:', error)
  }
}

// 2. 게시글 새로 등록하기 (POST API 연동)
const submitPost = async () => {
  if (!newPost.value.title || !newPost.value.summary || !newPost.value.author) {
    alert('모든 항목을 입력해주세요!')
    return
  }

  // 오늘 날짜 구하기 (YYYY.MM.DD)
  const today = new Date()
  const formattedDate = `${today.getFullYear()}.${String(today.getMonth() + 1).padStart(2, '0')}.${String(today.getDate()).padStart(2, '0')}`
  newPost.value.date = formattedDate

  try {
    await axios.post(API_URL, newPost.value)
    alert('게시글이 성공적으로 등록되었습니다.')
    
    // 폼 초기화 및 모달 닫기
    newPost.value = { title: '', summary: '', author: '', date: '' }
    showWriteModal.value = false
    
    // 목록 새로고침
    fetchPosts()
  } catch (error) {
    console.error('게시글 등록 실패:', error)
  }
}

// 컴포넌트가 마운트될 때 첫 로드 진행
onMounted(() => {
  fetchPosts()
})
</script>

<style scoped>
/* 기존 스타일은 그대로 유지하고 아래 모달 팝업 스타일을 추가합니다 */

.no-posts {
  padding: 40px 0;
  text-align: center;
  color: #868e96;
  font-size: 14px;
}

/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}
.modal-content {
  background-color: #fff;
  padding: 24px;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}
.modal-content h3 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: 800;
}
.modal-input {
  width: 100%;
  box-sizing: border-box;
  padding: 12px;
  border: 1.5px solid #dee2e6;
  border-radius: 8px;
  margin-bottom: 12px;
  outline: none;
  font-size: 14px;
}
.modal-textarea {
  width: 100%;
  box-sizing: border-box;
  height: 120px;
  padding: 12px;
  border: 1.5px solid #dee2e6;
  border-radius: 8px;
  margin-bottom: 16px;
  outline: none;
  font-size: 14px;
  resize: none;
}
.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
.btn-primary {
  background-color: #111;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
}
.btn-secondary {
  background-color: #e9ecef;
  color: #495057;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
}

/* 기존 PostBoard.vue의 스타일 ... */
.board-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  flex: 1;
}
.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}
.search-box {
  position: relative;
  flex: 1;
}
.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  color: #868e96;
}
.search-input {
  width: 100%;
  box-sizing: border-box;
  padding: 14px 16px 14px 44px;
  border: 1.5px solid #dee2e6;
  border-radius: 12px;
  font-size: 15px;
  background-color: #f8f9fa;
  outline: none;
  transition: all 0.2s;
}
.search-input:focus {
  background-color: #fff;
  border-color: #868e96;
}
.filter-actions {
  display: flex;
  gap: 10px;
}
.sort-select {
  padding: 0 16px;
  border: 1.5px solid #dee2e6;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  background-color: #fff;
  outline: none;
}
.filter-btn {
  padding: 0 16px;
  border: 1.5px solid #dee2e6;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  background-color: #fff;
  cursor: pointer;
  transition: background-color 0.2s;
}
.filter-btn:hover {
  background-color: #f8f9fa;
}
.post-list {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 8px;
}
.post-item {
  display: flex;
  gap: 24px;
  padding: 24px 0;
  border-bottom: 1.5px solid #f1f3f5;
}
.post-item:first-child { padding-top: 0; }
.post-item:last-child { border-bottom: none; }

.post-thumbnail {
  width: 120px;
  height: 120px;
  background-color: #f1f3f5;
  border: 1.5px solid #dee2e6;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: #adb5bd;
  flex-shrink: 0;
}
.post-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}
.post-title {
  font-size: 18px;
  font-weight: 800;
  color: #111;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.post-views {
  font-size: 13px;
  color: #868e96;
  font-weight: 500;
  flex-shrink: 0;
}
.post-summary {
  font-size: 14px;
  color: #495057;
  margin: 8px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}
.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}
.post-meta {
  font-size: 13px;
  color: #868e96;
}
.author {
  font-weight: 700;
  color: #495057;
}
.divider {
  margin: 0 8px;
  color: #dee2e6;
}
.post-buttons {
  display: flex;
  gap: 6px;
}
.action-btn {
  background: #fff;
  border: 1.5px solid #dee2e6;
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 13px;
  cursor: pointer;
  color: #495057;
  transition: all 0.2s;
}
.action-btn.score {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}
.action-btn:hover {
  background-color: #f8f9fa;
  border-color: #868e96;
}
.board-footer {
  margin-top: 24px;
  border-top: 1.5px solid #f1f3f5;
  padding-top: 24px;
}
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  margin-bottom: 24px;
}
.page-arrow, .page-num {
  background: none;
  border: none;
  width: 36px;
  height: 36px;
  font-size: 14px;
  font-weight: 600;
  color: #495057;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.page-num.active {
  background-color: #495057;
  color: #fff;
}
.page-num:hover:not(.active), .page-arrow:hover {
  background-color: #e9ecef;
}
.write-btn {
  width: 100%;
  padding: 16px 0;
  background-color: #f1f3f5;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 800;
  color: #212529;
  cursor: pointer;
  transition: background-color 0.2s;
}
.write-btn:hover {
  background-color: #e2e6ea;
}

@media (max-width: 640px) {
  .filter-bar {
    flex-direction: row;
    gap: 8px;
    margin-bottom: 12px;
  }
  .search-input {
    padding: 8px 10px 8px 30px;
    font-size: 12px;
    border-radius: 8px;
  }
  .search-icon {
    left: 10px;
    font-size: 12px;
  }
  .sort-select, .filter-btn {
    padding: 0 8px;
    font-size: 11px;
    border-radius: 8px;
  }
  .post-item {
    flex-direction: row;
    gap: 12px;
    padding: 12px 0;
  }
  .post-thumbnail {
    width: 64px;
    height: 64px;
    font-size: 20px;
    border-radius: 8px;
  }
  .post-title {
    font-size: 14px;
  }
  .post-views {
    font-size: 10px;
  }
  .post-summary {
    font-size: 11px;
    margin: 4px 0;
    -webkit-line-clamp: 1;
  }
  .post-meta {
    font-size: 10px;
  }
  .action-btn {
    padding: 3px 6px;
    font-size: 10px;
    border-radius: 4px;
  }
  .action-btn.score {
    gap: 3px;
  }
  .board-footer {
    margin-top: 12px;
    padding-top: 12px;
  }
  .pagination {
    margin-bottom: 12px;
    gap: 2px;
  }
  .page-arrow, .page-num {
    width: 28px;
    height: 28px;
    font-size: 11px;
    border-radius: 6px;
  }
  .write-btn {
    padding: 10px 0;
    font-size: 13px;
    border-radius: 8px;
  }
}
</style>