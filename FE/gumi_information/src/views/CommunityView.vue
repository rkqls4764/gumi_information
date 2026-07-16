<template>
  <div class="page-container">
    <h2>💬 자유 게시판</h2>
    <!-- 이전에 만든 FastAPI 연동 게시판 연결 -->
    <PostBoard />
  </div>
</template>

<script setup>
import PostBoard from '../components/PostBoard.vue'
</script>

<style scoped>
.page-container {
  padding: 16px 12px;
  max-width: 1000px;
  margin: 0 auto;
  box-sizing: border-box;
}

h2 {
  font-size: 1.3rem;
  font-weight: 800;
  margin-top: 4px;
  margin-bottom: 16px;
  text-align: left;
}

@media (min-width: 768px) {
  .page-container {
    padding: 20px;
  }
  h2 {
    font-size: 1.6rem;
  }
}
</style>