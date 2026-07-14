<template>
  <div class="page-container">
    <h2>🗺️ 여행지 지도 보기</h2>
    <div class="map-placeholder">
      <!-- 여기에 지도 API나 기존에 구현된 지도 관련 코드가 들어갑니다 -->
      <p>지도가 표시될 영역입니다.</p>
    </div>
  </div>
</template>

<style scoped>
.page-container { padding: 20px; max-width: 1200px; margin: 0 auto; }
.map-placeholder {
  width: 100%;
  height: 500px;
  background-color: #e9ecef;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #868e96;
}
</style>