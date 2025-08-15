<template>
  <div class="availability-form">
    <h3>Set Member Availability</h3>
    
    <div class="member-selector">
      <label for="member">Select Member:</label>
      <select id="member" v-model="selectedMemberId" @change="loadMemberAvailability">
        <option value="">Choose a member</option>
        <option v-for="member in members" :key="member.id" :value="member.id">
          {{ member.name }}
        </option>
      </select>
    </div>

    <div v-if="selectedMemberId" class="availability-section">
      <h4>Available Dates for {{ getSelectedMemberName() }}</h4>
      
      <div class="date-input-section">
        <div class="form-group">
          <label for="new_date">Add Date:</label>
          <input 
            id="new_date"
            v-model="newDate" 
            type="date" 
            @keyup.enter="addDate"
          />
          <button @click="addDate" :disabled="!newDate">Add Date</button>
        </div>
      </div>

      <div class="selected-dates">
        <h5>Selected Available Dates:</h5>
        <div v-if="selectedDates.length === 0" class="no-dates">
          No dates selected
        </div>
        <div v-else class="dates-list">
          <div v-for="date in sortedSelectedDates" :key="date" class="date-item">
            <span>{{ formatDate(date) }}</span>
            <button @click="removeDate(date)" class="remove-btn">×</button>
          </div>
        </div>
      </div>

      <div class="actions">
        <button @click="saveAvailability" :disabled="isSubmitting" class="save-btn">
          {{ isSubmitting ? 'Saving...' : 'Save Availability' }}
        </button>
        <button @click="clearAvailability" :disabled="isSubmitting" class="clear-btn">
          Clear All
        </button>
      </div>

      <div v-if="message" :class="messageClass">
        {{ message }}
      </div>
    </div>

    <!-- CSV Upload Section -->
    <AvailabilityCSVUpload @upload-completed="onCSVUploadCompleted" />

    <!-- Availability Overview Section -->
    <div class="overview-section">
      <AvailabilityOverview ref="availabilityOverviewRef" />
    </div>

    <!-- Shift Generation Section -->
    <div class="shift-generation-section">
      <h3>Generate Schedule</h3>
      <p>Once you've set availability for all members, you can generate the shift schedule:</p>
      <button @click="generateSchedule" :disabled="isGenerating" class="generate-btn">
        {{ isGenerating ? 'Generating Schedule...' : 'Generate Shift Schedule' }}
      </button>
      
      <div v-if="generationMessage" :class="generationMessageClass">
        {{ generationMessage }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AvailabilityOverview from './AvailabilityOverview.vue'
import AvailabilityCSVUpload from './AvailabilityCSVUpload.vue'

const members = ref([])
const selectedMemberId = ref('')
const selectedDates = ref([])
const newDate = ref('')
const isSubmitting = ref(false)
const message = ref('')
const messageClass = ref('')
const isGenerating = ref(false)
const generationMessage = ref('')
const generationMessageClass = ref('')
const availabilityOverviewRef = ref()

const emit = defineEmits(['scheduleGenerated'])

const sortedSelectedDates = computed(() => {
  return [...selectedDates.value].sort()
})

const loadMembers = async () => {
  try {
    const response = await fetch('/members/')
    if (response.ok) {
      members.value = await response.json()
    }
  } catch (error) {
    console.error('Error loading members:', error)
  }
}

const loadMemberAvailability = async () => {
  if (!selectedMemberId.value) {
    selectedDates.value = []
    return
  }
  
  try {
    const response = await fetch(`/availabilities/member/${selectedMemberId.value}`)
    if (response.ok) {
      const data = await response.json()
      selectedDates.value = data.dates
    } else {
      selectedDates.value = []
    }
  } catch (error) {
    console.error('Error loading member availability:', error)
    selectedDates.value = []
  }
}

const getSelectedMemberName = () => {
  const member = members.value.find(m => m.id == selectedMemberId.value)
  return member ? member.name : ''
}

const addDate = () => {
  if (!newDate.value) return
  
  if (!selectedDates.value.includes(newDate.value)) {
    selectedDates.value.push(newDate.value)
    newDate.value = ''
    message.value = ''
  } else {
    message.value = 'Date already selected'
    messageClass.value = 'error'
  }
}

const removeDate = (date) => {
  selectedDates.value = selectedDates.value.filter(d => d !== date)
}

const saveAvailability = async () => {
  if (!selectedMemberId.value) {
    message.value = 'Please select a member'
    messageClass.value = 'error'
    return
  }
  
  isSubmitting.value = true
  message.value = ''
  
  try {
    const response = await fetch('/availabilities/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        member_id: parseInt(selectedMemberId.value),
        dates: selectedDates.value
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      message.value = `Availability saved! ${result.count} dates set.`
      messageClass.value = 'success'
      
      // Refresh the overview
      if (availabilityOverviewRef.value) {
        availabilityOverviewRef.value.refreshData()
      }
    } else {
      const error = await response.json()
      message.value = `Error: ${error.detail || 'Failed to save availability'}`
      messageClass.value = 'error'
    }
  } catch (error) {
    message.value = 'Network error: Failed to save availability'
    messageClass.value = 'error'
  } finally {
    isSubmitting.value = false
  }
}

const clearAvailability = async () => {
  if (!selectedMemberId.value) return
  
  if (!confirm('Are you sure you want to clear all availability for this member?')) {
    return
  }
  
  isSubmitting.value = true
  
  try {
    const response = await fetch(`/availabilities/member/${selectedMemberId.value}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      selectedDates.value = []
      message.value = 'Availability cleared successfully'
      messageClass.value = 'success'
      
      // Refresh the overview
      if (availabilityOverviewRef.value) {
        availabilityOverviewRef.value.refreshData()
      }
    } else {
      message.value = 'Failed to clear availability'
      messageClass.value = 'error'
    }
  } catch (error) {
    message.value = 'Network error: Failed to clear availability'
    messageClass.value = 'error'
  } finally {
    isSubmitting.value = false
  }
}

const generateSchedule = async () => {
  isGenerating.value = true
  generationMessage.value = ''
  
  try {
    const response = await fetch('/shift-generation/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    
    if (response.ok) {
      const result = await response.json()
      generationMessage.value = `✅ ${result.message}\nTotal assignments: ${Object.keys(result.member_assignments).length} members`
      generationMessageClass.value = 'success'
      
      // Emit event to notify parent that schedule was generated
      emit('scheduleGenerated', result)
    } else {
      const error = await response.json()
      generationMessage.value = `❌ Error: ${error.detail || 'Failed to generate schedule'}`
      generationMessageClass.value = 'error'
    }
  } catch (error) {
    generationMessage.value = '❌ Network error: Failed to generate schedule'
    generationMessageClass.value = 'error'
  } finally {
    isGenerating.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

const onCSVUploadCompleted = (result) => {
  console.log('CSV upload completed:', result)
  
  // Show success message
  message.value = `CSV upload completed! Processed ${result.processed_dates} dates for ${result.processed_members} members with ${result.total_availabilities} availability records.`
  messageClass.value = 'success'
  
  // Refresh the availability data for the currently selected member
  if (selectedMemberId.value) {
    loadMemberAvailability()
  }
  
  // Refresh the overview
  if (availabilityOverviewRef.value) {
    availabilityOverviewRef.value.refreshData()
  }
}

onMounted(() => {
  loadMembers()
})
</script>

<style scoped>
.availability-form {
  max-width: 600px;
  margin: 20px 0;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.member-selector {
  margin-bottom: 20px;
}

.member-selector label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.member-selector select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.availability-section {
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.date-input-section {
  margin: 15px 0;
}

.form-group {
  display: flex;
  gap: 10px;
  align-items: end;
}

.form-group label {
  font-weight: bold;
  margin-bottom: 5px;
  white-space: nowrap;
}

.form-group input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-group button {
  padding: 8px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
}

.form-group button:hover:not(:disabled) {
  background-color: #0056b3;
}

.form-group button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.selected-dates {
  margin: 20px 0;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 5px;
}

.selected-dates h5 {
  margin-top: 0;
  margin-bottom: 10px;
}

.no-dates {
  color: #6c757d;
  font-style: italic;
}

.dates-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.date-item {
  display: flex;
  align-items: center;
  background-color: white;
  border: 1px solid #dee2e6;
  border-radius: 15px;
  padding: 5px 10px;
  font-size: 14px;
}

.remove-btn {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  margin-left: 8px;
  font-size: 16px;
  line-height: 1;
}

.remove-btn:hover {
  color: #a71e2a;
}

.actions {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.save-btn {
  background-color: #28a745;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn:hover:not(:disabled) {
  background-color: #218838;
}

.clear-btn {
  background-color: #dc3545;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.clear-btn:hover:not(:disabled) {
  background-color: #c82333;
}

.save-btn:disabled, .clear-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.success {
  color: green;
  margin-top: 10px;
}

.error {
  color: red;
  margin-top: 10px;
}

.shift-generation-section {
  margin-top: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 5px;
  border-left: 4px solid #007bff;
}

.shift-generation-section h3 {
  margin-top: 0;
  color: #007bff;
}

.shift-generation-section p {
  color: #6c757d;
  margin-bottom: 15px;
}

.generate-btn {
  background-color: #007bff;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
}

.generate-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.generate-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.overview-section {
  margin: 30px 0;
}
</style>