<template>
  <div class="availability-overview">
    <h3>Member Availability Overview</h3>
    
    <div v-if="loading" class="loading">Loading availability data...</div>
    
    <div v-else-if="availableDates.length === 0" class="no-dates">
      <p>No availability data found. Please upload availability data using CSV first.</p>
    </div>
    
    <div v-else-if="members.length === 0" class="no-members">
      <p>No members found. Please add members first.</p>
    </div>
    
    <div v-else class="overview-container">
      <div class="period-info">
        <p><strong>Available Dates:</strong> {{ availableDates.length }} dates from {{ formatDate(availableDates[0]) }} to {{ formatDate(availableDates[availableDates.length - 1]) }}</p>
      </div>

      <!-- Mobile view: List format -->
      <div class="mobile-view">
        <div v-for="member in members" :key="member.id" class="member-card">
          <h4 :class="{ 
                'male': member.gender === 'M', 
                'female': member.gender === 'F',
                'committee': member.is_committee
              }">
            {{ member.name }}
          </h4>
          <div class="availability-dates">
            <div v-if="getAvailabilityForMember(member.id).length === 0" class="no-availability">
              No available dates set
            </div>
            <div v-else class="date-chips">
              <span 
                v-for="date in getAvailabilityForMember(member.id)" 
                :key="date" 
                class="date-chip"
              >
                {{ formatDateShort(date) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Desktop view: Table format -->
      <div class="desktop-view">
        <div class="table-container">
          <table class="availability-table">
            <thead>
              <tr>
                <th class="member-header">Member</th>
                <th v-for="date in availableDates" :key="date" class="date-header">
                  <div class="date-cell">
                    <div class="date-day">{{ getDayOfWeek(date) }}</div>
                    <div class="date-number">{{ getDateNumber(date) }}</div>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="member in members" :key="member.id" class="member-row">
                <td class="member-name" 
                    :class="{ 
                      'male': member.gender === 'M', 
                      'female': member.gender === 'F',
                      'committee': member.is_committee
                    }">
                  {{ member.name }}
                </td>
                <td 
                  v-for="date in availableDates" 
                  :key="date" 
                  class="availability-cell"
                  :class="{ 'available': isMemberAvailable(member.id, date) }"
                >
                  <div class="availability-indicator">
                    {{ isMemberAvailable(member.id, date) ? '✓' : '' }}
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div class="legend">
          <div class="legend-section">
            <h5>Availability</h5>
            <div class="legend-item">
              <span class="legend-symbol available">✓</span>
              <span>Available</span>
            </div>
            <div class="legend-item">
              <span class="legend-symbol unavailable"></span>
              <span>Not Available</span>
            </div>
          </div>
          
          <div class="legend-section">
            <h5>Member Type</h5>
            <div class="legend-item">
              <span class="legend-symbol gender male-color">M</span>
              <span>Male</span>
            </div>
            <div class="legend-item">
              <span class="legend-symbol gender female-color">F</span>
              <span>Female</span>
            </div>
            <div class="legend-item">
              <span class="legend-symbol committee-style">C</span>
              <span>Committee Member</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Summary Statistics -->
      <div class="summary-stats">
        <h4>Summary</h4>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-label">Total Members:</span>
            <span class="stat-value">{{ members.length }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Available Days:</span>
            <span class="stat-value">{{ availableDates.length }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Avg. Availability per Member:</span>
            <span class="stat-value">{{ averageAvailability.toFixed(1) }} days</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Days with No Available Members:</span>
            <span class="stat-value">{{ daysWithNoAvailability }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const loading = ref(true)
const members = ref([])
const availabilities = ref([])

// Get all unique dates from availability data
const availableDates = computed(() => {
  const allDates = new Set()
  
  availabilities.value.forEach(memberAvail => {
    memberAvail.dates.forEach(date => {
      allDates.add(date)
    })
  })
  
  return Array.from(allDates).sort()
})

// Get availability dates for a specific member
const getAvailabilityForMember = (memberId) => {
  const memberAvailability = availabilities.value.find(a => a.member_id === memberId)
  return memberAvailability ? memberAvailability.dates : []
}

// Check if a member is available on a specific date
const isMemberAvailable = (memberId, date) => {
  const memberDates = getAvailabilityForMember(memberId)
  return memberDates.includes(date)
}

// Calculate average availability per member
const averageAvailability = computed(() => {
  if (members.value.length === 0) return 0
  const totalDays = availabilities.value.reduce((sum, avail) => sum + avail.dates.length, 0)
  return totalDays / members.value.length
})

// Count days with no available members
const daysWithNoAvailability = computed(() => {
  return availableDates.value.filter(date => {
    return !members.value.some(member => isMemberAvailable(member.id, date))
  }).length
})

const loadData = async () => {
  loading.value = true
  try {
    // Load members and availabilities in parallel
    const [membersRes, availRes] = await Promise.all([
      fetch('/members/'),
      fetch('/availabilities/')
    ])
    
    if (membersRes.ok) {
      members.value = await membersRes.json()
    }
    
    if (availRes.ok) {
      availabilities.value = await availRes.json()
    }
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

const formatDateShort = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const getDayOfWeek = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', { weekday: 'short' })
}

const getDateNumber = (dateString) => {
  return new Date(dateString).getDate()
}

const refreshData = () => {
  loadData()
}

onMounted(() => {
  loadData()
})

defineExpose({
  refreshData
})
</script>

<style scoped>
.availability-overview {
  margin: 20px 0;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #fafafa;
}

.loading, .no-dates, .no-members {
  text-align: center;
  padding: 20px;
  color: #6c757d;
}

.period-info {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #e3f2fd;
  border-radius: 5px;
  border-left: 4px solid #2196f3;
}

.period-info p {
  margin: 5px 0;
}

/* Mobile View */
.mobile-view {
  display: block;
}

.member-card {
  margin-bottom: 15px;
  padding: 15px;
  background-color: white;
  border-radius: 5px;
  border: 1px solid #ddd;
}

.member-card h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.no-availability {
  color: #888;
  font-style: italic;
}

.date-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.date-chip {
  background-color: #4caf50;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  white-space: nowrap;
}

/* Desktop View */
.desktop-view {
  display: none;
}

.table-container {
  overflow-x: auto;
  margin-bottom: 20px;
}

.availability-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.member-header, .date-header {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  padding: 8px;
  font-weight: bold;
  text-align: center;
}

.member-header {
  position: sticky;
  left: 0;
  z-index: 10;
  min-width: 120px;
}

.date-header {
  min-width: 50px;
}

.date-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.date-day {
  font-size: 10px;
  color: #666;
}

.date-number {
  font-size: 14px;
  font-weight: bold;
}

.member-row:nth-child(even) {
  background-color: #f9f9f9;
}

.member-name {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  padding: 12px 8px;
  font-weight: bold;
  position: sticky;
  left: 0;
  z-index: 5;
}

/* Gender-based styling */
.member-name.male, .member-card h4.male {
  color: #1976d2;
}

.member-name.female, .member-card h4.female {
  color: #e91e63;
}

/* Committee member styling */
.member-name.committee, .member-card h4.committee {
  font-weight: bold;
  text-decoration: underline;
}

.availability-cell {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
  width: 50px;
}

.availability-cell.available {
  background-color: #e8f5e8;
  color: #2e7d32;
}

.availability-indicator {
  font-weight: bold;
  font-size: 16px;
}

.legend {
  display: flex;
  gap: 40px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.legend-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-section h5 {
  margin: 0;
  font-size: 14px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.legend-symbol {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #ddd;
  border-radius: 3px;
  font-weight: bold;
}

.legend-symbol.available {
  background-color: #e8f5e8;
  color: #2e7d32;
}

.legend-symbol.unavailable {
  background-color: #f5f5f5;
}

.legend-symbol.gender {
  font-weight: bold;
  font-size: 14px;
}

.legend-symbol.male-color {
  background-color: #e3f2fd;
  color: #1976d2;
}

.legend-symbol.female-color {
  background-color: #fce4ec;
  color: #e91e63;
}

.legend-symbol.committee-style {
  background-color: #fff3e0;
  color: #f57c00;
  font-weight: bold;
}

.summary-stats {
  margin-top: 20px;
  padding: 15px;
  background-color: white;
  border-radius: 5px;
  border: 1px solid #ddd;
}

.summary-stats h4 {
  margin: 0 0 15px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.stat-label {
  color: #666;
}

.stat-value {
  font-weight: bold;
  color: #333;
}

/* Desktop breakpoint */
@media (min-width: 768px) {
  .mobile-view {
    display: none;
  }
  
  .desktop-view {
    display: block;
  }
}
</style>