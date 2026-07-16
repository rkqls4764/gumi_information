<!-- src/views/LocalInfoView.vue -->
<template>
  <div class="page">
    <main class="content">
      <div class="content-header">
        <h1>📅 캘린더</h1>
        <p>구미/경북 지역의 행사와 축제 일정을 확인해보세요.</p>
      </div>

      <div class="calendar-layout">
        <!-- Calendar column -->
        <section class="calendar-col">
          <p v-if="isLoading" class="status-text">일정을 불러오는 중...</p>
          <p v-else-if="loadError" class="status-text status-error">{{ loadError }}</p>

          <div class="calendar-controls">
            <div class="controls-left" v-if="viewMode !== '목록'">
              <button type="button" class="btn-outline" @click="goToday">오늘</button>
              <div class="navigation-arrows">
                <button type="button" class="btn-icon" @click="navigate(-1)" aria-label="이전">
                  <svg viewBox="0 0 24 24" fill="none"><path d="M15 6l-6 6 6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </button>
                <button type="button" class="btn-icon" @click="navigate(1)" aria-label="다음">
                  <svg viewBox="0 0 24 24" fill="none"><path d="M9 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </button>
              </div>
              <span class="month-label">
                {{ viewMode === '월' ? monthLabel : weekLabel }}
              </span>
            </div>
            <div class="controls-left" v-else>
              <span class="list-summary">전체 일정 {{ filteredEvents.length }}건</span>
            </div>

            <div class="view-toggle">
              <button
                v-for="v in viewModes"
                :key="v"
                type="button"
                class="view-toggle-btn"
                :class="{ active: viewMode === v }"
                @click="viewMode = v"
              >
                {{ v }}
              </button>
            </div>
          </div>

          <!-- Month view -->
          <div v-if="viewMode === '월'" class="calendar-grid">
            <div class="weekday-row">
              <span
                v-for="(d, i) in weekdays"
                :key="d"
                class="weekday"
                :class="{ 'weekday-sun': i === 0, 'weekday-sat': i === 6 }"
              >{{ d }}</span>
            </div>

            <div class="weeks">
              <div v-for="(week, wi) in calendarWeeks" :key="wi" class="week-row">
                <div
                  v-for="day in week"
                  :key="day.key"
                  class="day-cell"
                  :class="{ 'is-outside': !day.inCurrentMonth }"
                >
                  <span class="day-number" :class="{ today: day.isToday }">{{ day.date }}</span>
                  
                  <!-- 데스크톱용 일정 칩 (모바일에서 숨김) -->
                  <div class="day-events desktop-only">
                    <span
                      v-for="ev in day.events"
                      :key="ev.id"
                      class="event-chip"
                      :data-tooltip="ev.title"
                    >
                      <span class="event-chip-text">{{ ev.title }}</span>
                    </span>
                  </div>

                  <!-- 모바일용 미니 도트 인디케이터 (모바일에서만 표시) -->
                  <div class="day-dots-mobile mobile-only-flex">
                    <span 
                      v-for="ev in day.events.slice(0, 3)" 
                      :key="ev.id" 
                      class="dot-indicator"
                      :class="categoryClass(ev.category)"
                    ></span>
                    <span v-if="day.events.length > 3" class="dot-more">+</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Week view -->
          <div v-else-if="viewMode === '주'" class="calendar-grid week-grid">
            <div class="weekday-row week-weekday-row">
              <div v-for="d in weekDays" :key="d.key" class="week-weekday-cell">
                <span
                  class="weekday"
                  :class="{ 'weekday-sun': d.date.getDay() === 0, 'weekday-sat': d.date.getDay() === 6 }"
                >{{ weekdays[d.date.getDay()] }}</span>
                <span class="week-date-number" :class="{ today: d.isToday }">{{ d.date.getDate() }}</span>
              </div>
            </div>

            <div class="week-body-row">
              <div v-for="d in weekDays" :key="d.key" class="week-day-col">
                <div v-if="!d.events.length" class="week-empty">일정 없음</div>
                <div v-for="ev in d.events" :key="ev.id" class="week-event-card">
                  <span v-if="ev.time" class="week-event-time">{{ ev.time }}</span>
                  <span class="week-event-title">{{ ev.title }}</span>
                  <span class="week-event-location">{{ ev.location }}</span>
                  <span class="category-tag week-event-tag" :class="categoryClass(ev.category)">{{ ev.category }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- List view -->
          <div v-else class="calendar-grid list-view">
            <div v-if="!listGroups.length" class="list-empty">표시할 일정이 없습니다.</div>
            <div v-for="group in listGroups" :key="group.dateKey" class="list-group">
              <div class="list-group-header">{{ group.label }} ({{ group.weekday }})</div>
              <div class="list-group-events">
                <div v-for="ev in group.events" :key="ev.id" class="list-event-row">
                  <span class="category-tag" :class="categoryClass(ev.category)">{{ ev.category }}</span>
                  <div class="list-event-body">
                    <p class="list-event-title">{{ ev.title }}</p>
                    <p class="list-event-meta">{{ formatEventRange(ev) }} · {{ ev.location }}</p>
                  </div>
                  <button
                    type="button"
                    class="bookmark-btn"
                    :class="{ active: ev.bookmarked }"
                    @click="ev.bookmarked = !ev.bookmarked"
                    aria-label="북마크"
                  >
                    <svg viewBox="0 0 24 24" :fill="ev.bookmarked ? 'currentColor' : 'none'">
                      <path d="M6 4h12v16l-6-4-6 4V4z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 카테고리 필터 -->
          <div class="category-filter">
            <p class="filter-label">카테고리 필터</p>
            <div class="filter-options">
              <label class="filter-option">
                <input type="checkbox" :checked="allSelected" @change="toggleAll" />
                <span>전체</span>
              </label>
              <label v-for="cat in categoryList" :key="cat" class="filter-option">
                <input type="checkbox" v-model="selectedCategories" :value="cat" />
                <span>{{ cat }}</span>
              </label>
            </div>
          </div>
        </section>

        <!-- Sidebar -->
        <aside class="sidebar">
          <div class="sidebar-header">
            <h2>🔥 다가오는 일정</h2>
          </div>

          <ul class="upcoming-list">
            <li v-for="ev in upcomingEvents.slice(0, 6)" :key="ev.id" class="upcoming-item">
              <div class="date-badge">
                <span class="date-badge-day">{{ formatShortDate(ev.start) }}</span>
                <span class="date-badge-weekday">({{ weekdayOf(ev.start) }})</span>
              </div>

              <div class="upcoming-body">
                <p class="upcoming-title">{{ ev.title }}</p>
                <p class="upcoming-meta">{{ formatEventRange(ev) }} · {{ ev.location }}</p>
              </div>

              <div class="upcoming-actions">
                <span class="category-tag" :class="categoryClass(ev.category)">{{ ev.category }}</span>
              </div>
            </li>
          </ul>
        </aside>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

/* ---------------- Events data (fetched from backend) ---------------- */
// BE(main.py)의 GET /festivals 를 그대로 사용.
// 개발 중엔 http://localhost:8000, 배포 시엔 실제 API 주소로 바꿔주세요.
const API_BASE_URL = 'https://gumi-information.onrender.com' 

const events = reactive([])
const isLoading = ref(false)
const loadError = ref('')

async function loadEvents() {
  isLoading.value = true
  loadError.value = ''
  try {
    const res = await fetch(`${API_BASE_URL}/festivals`)
    if (!res.ok) throw new Error(`서버 응답 오류 (${res.status})`)
    const data = await res.json()
    events.splice(0, events.length, ...data.map((ev) => ({ ...ev, bookmarked: false })))
  } catch (err) {
    loadError.value = '일정을 불러오지 못했어요. 백엔드 서버가 켜져 있는지 확인해주세요.'
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

onMounted(loadEvents)

/* ---------------- Category filter ---------------- */
const categoryList = ['축제', '행사', '공연', '전시', '기타']
const selectedCategories = ref([...categoryList])

const allSelected = computed(() => selectedCategories.value.length === categoryList.length)

function toggleAll(e) {
  selectedCategories.value = e.target.checked ? [...categoryList] : []
}

const filteredEvents = computed(() =>
  events.filter((ev) => selectedCategories.value.includes(ev.category))
)

const categoryClassMap = {
  '축제': 'tag-festival',
  '행사': 'tag-event',
  '공연': 'tag-performance',
  '전시': 'tag-exhibition',
  '기타': 'tag-etc',
}

function categoryClass(category) {
  return categoryClassMap[category] || 'tag-etc'
}

/* ---------------- Calendar state & helpers ---------------- */
const weekdays = ['일', '월', '화', '수', '목', '금', '토']
const viewModes = ['월', '주', '목록']
const viewMode = ref('월')

const today = new Date()
const current = ref(new Date(today.getFullYear(), today.getMonth(), 1))

const viewYear = computed(() => current.value.getFullYear())
const viewMonth = computed(() => current.value.getMonth())

function navigate(delta) {
  if (viewMode.value === '월') {
    current.value = new Date(viewYear.value, viewMonth.value + delta, 1)
  } else if (viewMode.value === '주') {
    const d = new Date(current.value)
    d.setDate(d.getDate() + delta * 7)
    current.value = d
  }
}

function goToday() {
  current.value = new Date(today.getFullYear(), today.getMonth(), today.getDate())
}

const monthLabel = computed(() => `${viewYear.value}년 ${viewMonth.value + 1}월`)

function toDateKey(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function isSameDay(a, b) {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate()
}

const eventsByDate = computed(() => {
  const map = {}
  for (const ev of filteredEvents.value) {
    if (!map[ev.start]) map[ev.start] = []
    map[ev.start].push(ev)
  }
  return map
})

const calendarWeeks = computed(() => {
  const firstOfMonth = new Date(viewYear.value, viewMonth.value, 1)
  const startOffset = firstOfMonth.getDay()
  const gridStart = new Date(viewYear.value, viewMonth.value, 1 - startOffset)

  const weeks = []
  let cursor = new Date(gridStart)

  for (let w = 0; w < 6; w++) {
    const week = []
    for (let d = 0; d < 7; d++) {
      const dateObj = new Date(cursor)
      const key = toDateKey(dateObj)
      week.push({
        key,
        date: dateObj.getDate(),
        inCurrentMonth: dateObj.getMonth() === viewMonth.value,
        isToday: isSameDay(dateObj, today),
        events: eventsByDate.value[key] || [],
      })
      cursor.setDate(cursor.getDate() + 1)
    }
    weeks.push(week)
    if (cursor.getMonth() !== viewMonth.value && cursor > new Date(viewYear.value, viewMonth.value + 1, 0)) {
      if (weeks.length >= 4) break
    }
  }
  return weeks
})

const weekDays = computed(() => {
  const start = new Date(current.value)
  start.setDate(start.getDate() - start.getDay())

  const days = []
  for (let i = 0; i < 7; i++) {
    const dt = new Date(start)
    dt.setDate(start.getDate() + i)
    const key = toDateKey(dt)
    days.push({
      key,
      date: dt,
      isToday: isSameDay(dt, today),
      events: eventsByDate.value[key] || [],
    })
  }
  return days
})

const weekLabel = computed(() => {
  const start = weekDays.value[0].date
  const end = weekDays.value[6].date
  if (start.getMonth() === end.getMonth()) {
    return `${start.getMonth() + 1}월 ${start.getDate()}일 - ${end.getDate()}일`
  }
  return `${start.getMonth() + 1}월 ${start.getDate()}일 - ${end.getMonth() + 1}월 ${end.getDate()}일`
})

const listGroups = computed(() => {
  const map = {}
  for (const ev of filteredEvents.value) {
    if (!map[ev.start]) map[ev.start] = []
    map[ev.start].push(ev)
  }
  return Object.keys(map)
    .sort()
    .map((dateKey) => {
      const d = new Date(dateKey)
      return {
        dateKey,
        label: `${d.getMonth() + 1}월 ${d.getDate()}일`,
        weekday: weekdays[d.getDay()],
        events: map[dateKey],
      }
    })
})

const upcomingEvents = computed(() => {
  const todayKey = toDateKey(today)
  return filteredEvents.value
    .filter((ev) => ev.end >= todayKey || ev.start >= todayKey)
    .sort((a, b) => a.start.localeCompare(b.start))
})

function formatShortDate(dateStr) {
  const [, m, d] = dateStr.split('-')
  return `${m}.${d}`
}

function weekdayOf(dateStr) {
  const d = new Date(dateStr)
  return weekdays[d.getDay()]
}

function formatEventRange(ev) {
  if (ev.time) return `${formatShortDate(ev.start)} ${ev.time}`
  if (ev.start === ev.end) return formatShortDate(ev.start)
  return `${formatShortDate(ev.start)} ~ ${formatShortDate(ev.end)}`
}
</script>

<style scoped>
/* 전역 box-sizing 강제로 레이아웃 보존 */
*, *::before, *::after { 
  box-sizing: border-box; 
}

/* 반응형 디스플레이 전환 유틸리티 */
.desktop-only {
  display: flex !important;
}
.mobile-only-flex {
  display: none !important;
}

.page {
  --brand-purple: #7c5cfc;
  --brand-purple-dark: #6a48e8;
  --brand-purple-bg: #f1ebff;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #1a1a1a;
  background: #fff;
  min-height: 100vh;
  width: 100%;
  overflow-x: hidden; /* 가로 스크롤 완전 방지 */
}

.content {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 20px 60px;
}

.content-header h1 {
  font-size: 24px;
  font-weight: 800;
  margin: 0 0 6px;
  letter-spacing: -0.5px;
}

.content-header p {
  font-size: 13px;
  color: #777;
  margin: 0 0 20px;
}

.calendar-layout {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
  align-items: start;
  width: 100%;
}

.calendar-col {
  width: 100%;
  min-width: 0; /* flex/grid 삐져나감 제어 속성 */
}

/* ---- Controls ---- */
.calendar-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
  width: 100%;
}

.controls-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.navigation-arrows {
  display: flex;
  gap: 4px;
}

.btn-outline {
  padding: 8px 14px;
  font-size: 13px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  font-weight: 600;
}

.btn-outline:hover {
  background: #f8f9fa;
}

.btn-icon {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  color: #495057;
}

.btn-icon svg {
  width: 18px;
  height: 18px;
}

.btn-icon:hover {
  background: #f8f9fa;
}

.month-label {
  font-size: 16px;
  font-weight: 800;
  padding-left: 4px;
  color: #111;
}

.view-toggle {
  display: flex;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.view-toggle-btn {
  padding: 8px 14px;
  font-size: 13px;
  background: #fff;
  border: none;
  border-left: 1px solid #dee2e6;
  color: #495057;
  cursor: pointer;
  font-weight: 600;
}

.view-toggle-btn:first-child {
  border-left: none;
}

.view-toggle-btn.active {
  background: #1a1a1a;
  color: #fff;
}

/* ---- Calendar grid ---- */
.calendar-grid {
  width: 100%;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  background: #fff;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.weekday {
  text-align: center;
  padding: 12px 0;
  font-size: 13px;
  color: #868e96;
  font-weight: 700;
}

.weekday-sun { color: #fa5252; }
.weekday-sat { color: #228be6; }

.week-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  width: 100%;
}

.week-row + .week-row {
  border-top: 1px solid #e9ecef;
}

.day-cell {
  min-height: 110px;
  padding: 8px;
  border-left: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0; /* 가로 잘림 방지를 위한 한계치 제어 */
  overflow: hidden;
}

.day-cell:first-child {
  border-left: none;
}

.day-cell.is-outside .day-number {
  color: #ced4da;
}

.day-number {
  font-size: 13px;
  font-weight: 700;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: #343a40;
}

.day-number.today {
  background: #1a1a1a;
  color: #fff;
}

.day-events {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.event-chip {
  background: var(--brand-purple-bg);
  color: var(--brand-purple-dark);
  font-size: 11px;
  font-weight: 700;
  padding: 3px 6px;
  border-radius: 4px;
  max-width: 100%;
  min-width: 0;
  position: relative;
  cursor: pointer;
}

.event-chip-text {
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.event-chip:hover::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 6px;
  background: #1a1a1a;
  color: #fff;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 50;
  pointer-events: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* ---- Week view ---- */
.week-weekday-row {
  grid-template-columns: repeat(7, 1fr);
}

.week-weekday-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 0;
}

.week-date-number {
  font-size: 14px;
  font-weight: 700;
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.week-date-number.today {
  background: #1a1a1a;
  color: #fff;
}

.week-body-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  min-height: 400px;
  width: 100%;
}

.week-day-col {
  border-left: 1px solid #e9ecef;
  padding: 8px 4px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.week-day-col:first-child {
  border-left: none;
}

.week-empty {
  font-size: 11px;
  color: #adb5bd;
  text-align: center;
  margin-top: 16px;
}

.week-event-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.01);
  min-width: 0;
}

.week-event-time {
  font-size: 10px;
  color: #495057;
  font-weight: 700;
}

.week-event-title {
  font-size: 12px;
  font-weight: 800;
  color: #111;
  line-height: 1.3;
}

.week-event-location {
  font-size: 10px;
  color: #868e96;
}

.week-event-tag {
  align-self: flex-start;
  transform: scale(0.9);
  transform-origin: left;
}

/* ---- List view ---- */
.list-summary {
  font-size: 14px;
  font-weight: 700;
  color: #495057;
}

.list-view {
  padding: 16px;
}

.list-empty {
  padding: 60px 0;
  text-align: center;
  font-size: 13px;
  color: #adb5bd;
}

.list-group + .list-group {
  margin-top: 24px;
}

.list-group-header {
  font-size: 14px;
  font-weight: 800;
  padding: 0 0 8px;
  border-bottom: 1.5px solid #f1f3f5;
  margin-bottom: 12px;
  color: #111;
}

.list-group-events {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.list-event-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #f1f3f5;
  border-radius: 10px;
  background: #fafafa;
  transition: all 0.2s ease;
}

.list-event-row:hover {
  border-color: #dee2e6;
  background: #fff;
}

.list-event-body {
  flex: 1;
  min-width: 0;
}

.list-event-title {
  font-size: 14px;
  font-weight: 800;
  margin: 0 0 3px;
  color: #111;
}

.list-event-meta {
  font-size: 12px;
  color: #868e96;
  margin: 0;
}

/* ---- Status text ---- */
.status-text {
  font-size: 13px;
  color: #868e96;
  margin: 0 0 12px;
}
.status-error { color: #fa5252; }

/* ---- Category filter ---- */
.category-filter {
  margin-top: 24px;
  width: 100%;
}

.filter-label {
  font-size: 13px;
  font-weight: 800;
  margin: 0 0 12px;
  color: #495057;
  text-transform: uppercase;
}

.filter-options {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.filter-option {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #495057;
  cursor: pointer;
  font-weight: 600;
}

.filter-option input {
  width: 16px;
  height: 16px;
  accent-color: var(--brand-purple);
  cursor: pointer;
}

/* ---- Sidebar ---- */
.sidebar {
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 24px;
  background: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
  width: 100%;
}

.sidebar-header h2 {
  font-size: 15px;
  font-weight: 800;
  margin: 0;
  color: #111;
}

.upcoming-list {
  list-style: none;
  margin: 12px 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upcoming-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
}

.upcoming-item + .upcoming-item {
  border-top: 1px solid #f1f3f5;
}

.date-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 46px;
  background: #f8f9fa;
  padding: 6px;
  border-radius: 8px;
}

.date-badge-day {
  font-size: 12px;
  font-weight: 800;
  color: var(--brand-purple);
}

.date-badge-weekday {
  font-size: 10px;
  color: #868e96;
  font-weight: 600;
}

.upcoming-body {
  flex: 1;
  min-width: 0;
}

.upcoming-title {
  font-size: 13px;
  font-weight: 800;
  margin: 0 0 3px;
  color: #111;
}

.upcoming-meta {
  font-size: 11px;
  color: #868e96;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.category-tag {
  font-size: 11px;
  font-weight: 700;
  background: #f1f3f5;
  color: #495057;
  padding: 4px 8px;
  border-radius: 20px;
  white-space: nowrap;
}

.category-tag.tag-festival {
  background: var(--brand-purple-bg);
  color: var(--brand-purple-dark);
}

.category-tag.tag-event {
  background: #fff3d6;
  color: #d9480f;
}

.category-tag.tag-performance {
  background: #e7f5ff;
  color: #1c7ed6;
}

.category-tag.tag-exhibition {
  background: #e6fcf5;
  color: #0ca678;
}

.category-tag.tag-etc {
  background: #f1f3f5;
  color: #868e96;
}

.bookmark-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #dee2e6;
  padding: 8px;
}

.bookmark-btn svg {
  width: 18px;
  height: 18px;
}

.bookmark-btn.active {
  color: #111;
}

/* ==============================================
   📱 모바일 디바이스 최적화 미디어 쿼리 (max-width: 640px)
   ============================================== */
@media (max-width: 640px) {
  .desktop-only {
    display: none !important;
  }
  .mobile-only-flex {
    display: flex !important;
  }

  /* 1. 컨텐트 바깥 좌우 패딩을 10px로 축소하여 가로 확장 */
  .content {
    padding: 16px 10px 40px;
  }

  .content-header h1 {
    font-size: 20px;
  }
  .content-header p {
    font-size: 12px;
    margin-bottom: 16px;
  }

  /* 2. 가로폭 완전 전면 보장 */
  .calendar-layout {
    grid-template-columns: 100%;
    gap: 20px;
    width: 100%;
  }

  .calendar-col {
    width: 100%;
  }

  .calendar-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
    width: 100%;
  }

  .controls-left {
    justify-content: space-between;
    width: 100%;
  }

  .month-label {
    font-size: 15px;
  }

  .view-toggle {
    width: 100%;
  }

  .view-toggle-btn {
    flex: 1;
    text-align: center;
    padding: 10px 0;
  }

  /* 3. 모바일 그리드가 화면 바깥으로 튀어나가지 않도록 제어 */
  .calendar-grid {
    width: 100%;
    max-width: 100%;
    table-layout: fixed;
  }

  .weekday-row, .weeks, .week-row {
    width: 100%;
    max-width: 100%;
  }

  .weekday-row {
    grid-template-columns: repeat(7, 1fr);
  }

  .week-row {
    grid-template-columns: repeat(7, 1fr);
  }

  .day-cell {
    min-height: 52px;
    padding: 4px 2px;
    align-items: center;
    justify-content: space-between;
    min-width: 0; /* 중요: 셀 가두기 */
    overflow: hidden;
  }

  .day-number {
    font-size: 11px;
    width: 18px;
    height: 18px;
  }

  /* 모바일용 일정 점(Dot) 인디케이터 */
  .day-dots-mobile {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 2px;
    width: 100%;
    min-height: 6px;
  }

  .dot-indicator {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background-color: #adb5bd;
    flex-shrink: 0;
  }
  .dot-indicator.tag-festival { background-color: var(--brand-purple); }
  .dot-indicator.tag-event { background-color: #f76707; }
  .dot-indicator.tag-performance { background-color: #228be6; }
  .dot-indicator.tag-exhibition { background-color: #12b886; }
  .dot-indicator.tag-etc { background-color: #868e96; }

  .dot-more {
    font-size: 8px;
    color: #868e96;
    font-weight: 700;
    line-height: 1;
  }

  /* 주(Week) 뷰 가로 크기 붕괴 방지 */
  .week-weekday-row {
    width: 100%;
  }
  .week-date-number {
    font-size: 12px;
    width: 20px;
    height: 20px;
  }
  .week-body-row {
    min-height: 240px;
    width: 100%;
  }
  .week-day-col {
    padding: 4px 1px;
    min-width: 0;
  }
  .week-event-card {
    padding: 4px 2px;
    border-radius: 4px;
    min-width: 0;
  }
  .week-event-title {
    font-size: 9px;
    line-height: 1.2;
    word-break: break-all;
  }
  .week-event-location {
    display: none;
  }

  /* 카테고리 필터 미세 조정 */
  .filter-options {
    gap: 10px;
  }
  .filter-option {
    font-size: 12px;
  }

  /* 다가오는 일정 하단부 리스타일링 */
  .sidebar {
    padding: 16px;
    border-radius: 12px;
    width: 100%;
  }
  .upcoming-item {
    background: #f8f9fa;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 6px;
    border: none !important;
  }
  .upcoming-title {
    font-size: 12px;
  }
  .upcoming-meta {
    font-size: 10px;
  }
}
</style>