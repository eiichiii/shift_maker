<template>
  <div>
    <h1>Shift Maker</h1>
    
    <div class="tabs">
      <button 
        @click="activeTab = 'schedule'" 
        :class="{ active: activeTab === 'schedule' }"
      >
        Schedule
      </button>
      <button 
        @click="activeTab = 'members'" 
        :class="{ active: activeTab === 'members' }"
      >
        Members
      </button>
      <button 
        @click="activeTab = 'availability'" 
        :class="{ active: activeTab === 'availability' }"
      >
        Availability
      </button>
    </div>
    
    <div v-if="activeTab === 'schedule'">
      <ScheduleTable ref="scheduleTableRef" />
    </div>
    
    <div v-if="activeTab === 'members'">
      <MemberForm @member-added="onMemberAdded" @members-uploaded="onMembersUploaded" />
      <MemberList ref="memberListRef" />
    </div>
    
    
    <div v-if="activeTab === 'availability'">
      <AvailabilityForm @schedule-generated="onScheduleGenerated" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ScheduleTable from './components/ScheduleTable.vue'
import MemberForm from './components/MemberForm.vue'
import MemberList from './components/MemberList.vue'
import AvailabilityForm from './components/AvailabilityForm.vue'

const activeTab = ref('schedule')
const memberListRef = ref()
const scheduleTableRef = ref()

const onMemberAdded = () => {
  if (memberListRef.value) {
    memberListRef.value.refreshMembers()
  }
}

const onMembersUploaded = (result) => {
  console.log('Members uploaded:', result)
  if (memberListRef.value) {
    memberListRef.value.refreshMembers()
  }
}


const onScheduleGenerated = (result) => {
  console.log('Schedule generated:', result)
  // Switch to Schedule tab to show the generated schedule
  activeTab.value = 'schedule'
  
  // Refresh schedule table if it exists
  setTimeout(() => {
    if (scheduleTableRef.value && scheduleTableRef.value.refreshSchedule) {
      scheduleTableRef.value.refreshSchedule()
    }
  }, 100)
}
</script>

<style scoped>
.tabs {
  display: flex;
  margin: 20px 0;
  border-bottom: 1px solid #ccc;
}

.tabs button {
  padding: 10px 20px;
  border: none;
  background: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  font-size: 16px;
}

.tabs button:hover {
  background-color: #f5f5f5;
}

.tabs button.active {
  border-bottom-color: #007bff;
  color: #007bff;
  font-weight: bold;
}
</style>
