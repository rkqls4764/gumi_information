<template>
  <div class="page">
    <main class="content">
      <div class="content-header">
        <h1>캘린더</h1>
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
              <button type="button" class="btn-icon" @click="navigate(-1)" aria-label="이전">
                <svg viewBox="0 0 24 24" fill="none"><path d="M15 6l-6 6 6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
              <button type="button" class="btn-icon" @click="navigate(1)" aria-label="다음">
                <svg viewBox="0 0 24 24" fill="none"><path d="M9 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
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
              <span v-for="d in weekdays" :key="d" class="weekday">{{ d }}</span>
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
                  <div class="day-events">
                    <span
                      v-for="ev in day.events"
                      :key="ev.id"
                      class="event-chip"
                      :data-tooltip="ev.title"
                    >
                      <span class="event-chip-text">{{ ev.title }}</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Week view -->
          <div v-else-if="viewMode === '주'" class="calendar-grid week-grid">
            <div class="weekday-row week-weekday-row">
              <div v-for="d in weekDays" :key="d.key" class="week-weekday-cell">
                <span class="weekday">{{ weekdays[d.date.getDay()] }}</span>
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
                  <span class="category-tag week-event-tag">{{ ev.category }}</span>
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
                  <span class="category-tag">{{ ev.category }}</span>
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

          <div class="category-filter">
            <p class="filter-label">카테고리 필터</p>
            <div class="filter-options">
              <label class="filter-option">
                <input type="checkbox" :checked="allSelected" @change="toggleAll" />
                전체
              </label>
              <label v-for="cat in categoryList" :key="cat" class="filter-option">
                <input type="checkbox" v-model="selectedCategories" :value="cat" />
                {{ cat }}
              </label>
            </div>
          </div>
        </section>

        <!-- Sidebar -->
        <aside class="sidebar">
          <div class="sidebar-header">
            <h2>다가오는 일정</h2>
          </div>

          <ul class="upcoming-list">
            <li v-for="ev in upcomingEvents" :key="ev.id" class="upcoming-item">
              <div class="date-badge">
                <span class="date-badge-day">{{ formatShortDate(ev.start) }}</span>
                <span class="date-badge-weekday">({{ weekdayOf(ev.start) }})</span>
              </div>

              <div class="upcoming-body">
                <p class="upcoming-title">{{ ev.title }}</p>
                <p class="upcoming-meta">{{ formatEventRange(ev) }} · {{ ev.location }}</p>
              </div>

              <div class="upcoming-actions">
                <span class="category-tag">{{ ev.category }}</span>
              </div>
            </li>
          </ul>
        </aside>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, h, onMounted } from 'vue'

/* ---------------- Events data (fetched from backend) ---------------- */
// BE(main.py)의 GET /festivals 를 그대로 사용.
// 개발 중엔 http://localhost:8000, 배포 시엔 실제 API 주소로 바꿔주세요.
const API_BASE_URL = 'http://localhost:8000'

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

/* ---------------- Top nav ---------------- */
const CalendarIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'none' }, [
  h('rect', { x: 3, y: 5, width: 18, height: 16, rx: 2, stroke: 'currentColor', 'stroke-width': 1.8 }),
  h('path', { d: 'M3 9h18M8 3v4M16 3v4', stroke: 'currentColor', 'stroke-width': 1.8, 'stroke-linecap': 'round' }),
])
const MapIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'none' }, [
  h('path', { d: 'M9 4L3 6v14l6-2 6 2 6-2V4l-6 2-6-2z', stroke: 'currentColor', 'stroke-width': 1.8, 'stroke-linejoin': 'round' }),
  h('path', { d: 'M9 4v14M15 6v14', stroke: 'currentColor', 'stroke-width': 1.8 }),
])
const PinIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'none' }, [
  h('path', { d: 'M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z', stroke: 'currentColor', 'stroke-width': 1.8, 'stroke-linejoin': 'round' }),
  h('circle', { cx: 12, cy: 10, r: 2.5, stroke: 'currentColor', 'stroke-width': 1.8 }),
])
const ChatIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'none' }, [
  h('path', { d: 'M4 12a8 8 0 1 1 3.2 6.4L4 20l1.3-3.6A7.96 7.96 0 0 1 4 12z', stroke: 'currentColor', 'stroke-width': 1.8, 'stroke-linejoin': 'round' }),
])

const tabs = [
  { key: 'calendar', label: '캘린더', icon: CalendarIcon },
  { key: 'info', label: '지역 정보', icon: MapIcon },
  { key: 'map', label: '지도', icon: PinIcon },
  { key: 'community', label: '커뮤니티', icon: ChatIcon },
]
const activeTab = ref('calendar')

/* ---------------- Category filter ---------------- */
const categoryList = ['축제', '행사', '공연', '전시', '기타']
const selectedCategories = ref([...categoryList]) // default: show everything

const allSelected = computed(() => selectedCategories.value.length === categoryList.length)

function toggleAll(e) {
  selectedCategories.value = e.target.checked ? [...categoryList] : []
}

const filteredEvents = computed(() =>
  events.filter((ev) => selectedCategories.value.includes(ev.category))
)

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
  // 목록 뷰는 날짜 이동 없이 필터된 전체 일정을 보여줍니다.
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

// Events are shown as a chip only on their start date (matches the design).
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
  const startOffset = firstOfMonth.getDay() // 0=Sun
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
    // stop after the week that covers the last day of the month, once we've completed a full row
    if (cursor.getMonth() !== viewMonth.value && cursor > new Date(viewYear.value, viewMonth.value + 1, 0)) {
      if (weeks.length >= 4) break
    }
  }
  return weeks
})

// 7 days (Sun–Sat) of the week that contains `current`
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
    return `${start.getFullYear()}년 ${start.getMonth() + 1}월 ${start.getDate()}일 - ${end.getDate()}일`
  }
  return `${start.getFullYear()}년 ${start.getMonth() + 1}월 ${start.getDate()}일 - ${end.getMonth() + 1}월 ${end.getDate()}일`
})

// Flat, chronological list of all events matching the active category filter
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

/* ---------------- Sidebar: upcoming events ---------------- */
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
* { box-sizing: border-box; }

.page {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #1a1a1a;
  background: #fff;
  min-height: 100vh;
}

/* ---- Top nav ---- */
.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 40px;
  border-bottom: 1px solid #eee;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-icon {
  width: 32px;
  height: 32px;
  color: #1a1a1a;
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.brand-text strong {
  font-size: 18px;
}

.brand-text span {
  font-size: 12px;
  color: #9a9a9a;
}

.nav-tabs {
  display: flex;
  gap: 32px;
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  font-size: 14px;
  color: #9a9a9a;
  cursor: pointer;
  padding: 6px 2px;
  border-bottom: 2px solid transparent;
}

.nav-tab-icon {
  width: 16px;
  height: 16px;
}

.nav-tab.active {
  color: #1a1a1a;
  font-weight: 600;
  border-bottom-color: #1a1a1a;
}

/* ---- Content ---- */
.content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 40px 80px;
}

.content-header h1 {
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 6px;
}

.content-header p {
  font-size: 14px;
  color: #9a9a9a;
  margin: 0 0 24px;
}

.calendar-layout {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 24px;
  align-items: start;
}

/* ---- Controls ---- */
.calendar-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.controls-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-outline {
  padding: 8px 14px;
  font-size: 13px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
}

.btn-outline:hover {
  background: #f7f7f7;
}

.btn-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  color: #4a4a4a;
}

.btn-icon svg {
  width: 16px;
  height: 16px;
}

.btn-icon:hover {
  background: #f7f7f7;
}

.month-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 16px;
  font-weight: 700;
  padding: 8px 6px;
}

.chevron-down {
  width: 16px;
  height: 16px;
  color: #9a9a9a;
}

.view-toggle {
  display: flex;
  border: 1px solid #ddd;
  border-radius: 6px;
  overflow: hidden;
}

.view-toggle-btn {
  padding: 8px 16px;
  font-size: 13px;
  background: #fff;
  border: none;
  border-left: 1px solid #ddd;
  color: #6a6a6a;
  cursor: pointer;
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
  border: 1px solid #e5e5e5;
  border-radius: 10px;
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: #fafafa;
  border-bottom: 1px solid #e5e5e5;
  border-radius: 9px 9px 0 0;
}

.weekday {
  text-align: center;
  padding: 10px 0;
  font-size: 13px;
  color: #9a9a9a;
  font-weight: 600;
}

.week-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.week-row + .week-row {
  border-top: 1px solid #e5e5e5;
}

.day-cell {
  min-height: 110px;
  padding: 10px;
  border-left: 1px solid #e5e5e5;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.day-cell:first-child {
  border-left: none;
}

.day-cell.is-outside .day-number {
  color: #ccc;
}

.day-number {
  font-size: 14px;
  font-weight: 600;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
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
  background: #f0f0f0;
  color: #4a4a4a;
  font-size: 11px;
  padding: 4px 6px;
  border-radius: 4px;
  max-width: 100%;
  min-width: 0;
  box-sizing: border-box;
  position: relative;
  cursor: default;
  /* overflow: hidden을 여기 두면 아래 :hover::after 툴팁까지 같이 잘려서 안 보임 */
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
  left: 0;
  margin-bottom: 4px;
  background: #1a1a1a;
  color: #fff;
  padding: 5px 9px;
  border-radius: 5px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 30;
  pointer-events: none;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

/* ---- Week view ---- */
.week-weekday-row {
  grid-template-columns: repeat(7, 1fr);
}

.week-weekday-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 10px 0;
}

.week-date-number {
  font-size: 15px;
  font-weight: 700;
  width: 28px;
  height: 28px;
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
  min-height: 360px;
}

.week-day-col {
  border-left: 1px solid #e5e5e5;
  padding: 10px 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.week-day-col:first-child {
  border-left: none;
}

.week-empty {
  font-size: 11px;
  color: #ccc;
  text-align: center;
  margin-top: 12px;
}

.week-event-card {
  display: flex;
  flex-direction: column;
  gap: 3px;
  background: #f7f7f7;
  border-radius: 6px;
  padding: 8px;
}

.week-event-time {
  font-size: 11px;
  color: #6a6a6a;
  font-weight: 600;
}

.week-event-title {
  font-size: 12px;
  font-weight: 700;
  color: #1a1a1a;
}

.week-event-location {
  font-size: 11px;
  color: #9a9a9a;
}

.week-event-tag {
  align-self: flex-start;
  margin-top: 2px;
}

/* ---- List view ---- */
.list-summary {
  font-size: 14px;
  font-weight: 600;
  color: #4a4a4a;
}

.list-view {
  padding: 8px 20px 20px;
}

.list-empty {
  padding: 40px 0;
  text-align: center;
  font-size: 13px;
  color: #bbb;
}

.list-group + .list-group {
  margin-top: 20px;
}

.list-group-header {
  font-size: 14px;
  font-weight: 700;
  padding: 12px 0 8px;
  border-bottom: 1px solid #eee;
  margin-bottom: 10px;
}

.list-group-events {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.list-event-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 8px;
}

.list-event-body {
  flex: 1;
  min-width: 0;
}

.list-event-title {
  font-size: 14px;
  font-weight: 700;
  margin: 0 0 4px;
}

.list-event-meta {
  font-size: 12px;
  color: #9a9a9a;
  margin: 0;
}

/* ---- Status text (loading/error) ---- */
.status-text {
  font-size: 13px;
  color: #9a9a9a;
  margin: 0 0 12px;
}

.status-error {
  color: #d9534f;
}

/* ---- Category filter ---- */
.category-filter {
  margin-top: 20px;
}

.filter-label {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 10px;
}

.filter-options {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.filter-option {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #4a4a4a;
  cursor: pointer;
}

.filter-option input {
  width: 15px;
  height: 15px;
  accent-color: #1a1a1a;
  cursor: pointer;
}

/* ---- Sidebar ---- */
.sidebar {
  border: 1px solid #e5e5e5;
  border-radius: 10px;
  padding: 20px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.sidebar-header h2 {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
}

.link-btn {
  display: flex;
  align-items: center;
  gap: 2px;
  background: none;
  border: none;
  font-size: 12px;
  color: #9a9a9a;
  cursor: pointer;
}

.link-btn svg {
  width: 14px;
  height: 14px;
}

.upcoming-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.upcoming-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 8px;
}

.date-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 52px;
  padding: 6px 4px;
  border: 1px solid #e5e5e5;
  border-radius: 6px;
}

.date-badge-day {
  font-size: 13px;
  font-weight: 700;
}

.date-badge-weekday {
  font-size: 11px;
  color: #9a9a9a;
}

.upcoming-body {
  flex: 1;
  min-width: 0;
}

.upcoming-title {
  font-size: 14px;
  font-weight: 700;
  margin: 0 0 4px;
}

.upcoming-meta {
  font-size: 12px;
  color: #9a9a9a;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.upcoming-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.category-tag {
  font-size: 11px;
  background: #f0f0f0;
  color: #4a4a4a;
  padding: 3px 8px;
  border-radius: 999px;
  white-space: nowrap;
}

.bookmark-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #bbb;
  padding: 0;
}

.bookmark-btn svg {
  width: 16px;
  height: 16px;
}

.bookmark-btn.active {
  color: #1a1a1a;
}

/* ---- Floating action button ---- */
.fab {
  position: fixed;
  right: 32px;
  bottom: 32px;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #1a1a1a;
  color: #fff;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.fab svg {
  width: 22px;
  height: 22px;
}

@media (max-width: 960px) {
  .calendar-layout {
    grid-template-columns: 1fr;
  }
}
</style>