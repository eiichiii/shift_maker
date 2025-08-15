<template>
  <div class="member-list">
    <h3>Members</h3>
    <div v-if="loading">Loading members...</div>
    <div v-else-if="members.length === 0">No members found.</div>
    <table v-else>
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Gender</th>
          <th>Committee</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="member in members" :key="member.id">
          <td>{{ member.id }}</td>
          <td>{{ member.name }}</td>
          <td>{{ member.gender === 'M' ? 'Male' : 'Female' }}</td>
          <td>{{ member.is_committee ? 'Yes' : 'No' }}</td>
          <td>
            <button 
              @click="deleteMember(member.id)" 
              class="delete-btn"
              :disabled="deleting === member.id"
            >
              {{ deleting === member.id ? 'Deleting...' : 'Delete' }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const members = ref([])
const loading = ref(true)
const deleting = ref(null)

const loadMembers = async () => {
  loading.value = true
  try {
    const response = await fetch('/members/')
    if (response.ok) {
      members.value = await response.json()
    } else {
      console.error('Failed to load members')
    }
  } catch (error) {
    console.error('Error loading members:', error)
  } finally {
    loading.value = false
  }
}

const deleteMember = async (memberId) => {
  if (!confirm('Are you sure you want to delete this member?')) {
    return
  }
  
  deleting.value = memberId
  try {
    const response = await fetch(`/members/${memberId}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      // Remove member from local list
      members.value = members.value.filter(member => member.id !== memberId)
    } else {
      console.error('Failed to delete member')
      alert('Failed to delete member')
    }
  } catch (error) {
    console.error('Error deleting member:', error)
    alert('Network error: Failed to delete member')
  } finally {
    deleting.value = null
  }
}

const refreshMembers = () => {
  loadMembers()
}

onMounted(() => {
  loadMembers()
})

defineExpose({
  refreshMembers
})
</script>

<style scoped>
.member-list {
  margin: 20px 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

th, td {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

th {
  background-color: #f5f5f5;
  font-weight: bold;
}

tr:nth-child(even) {
  background-color: #f9f9f9;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
}

.delete-btn:hover:not(:disabled) {
  background-color: #c82333;
}

.delete-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}
</style>