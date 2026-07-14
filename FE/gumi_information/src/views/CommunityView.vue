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
.page-container { padding: 20px; max-width: 1000px; margin: 0 auto; }
</style>