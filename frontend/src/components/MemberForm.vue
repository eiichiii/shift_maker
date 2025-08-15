<template>
  <div class="member-form">
    <h3>Add New Member</h3>
    <form @submit.prevent="submitMember">
      <div class="form-group">
        <label for="name">Name:</label>
        <input 
          id="name"
          v-model="form.name" 
          type="text" 
          required 
          placeholder="Enter member name"
        />
      </div>
      
      <div class="form-group">
        <label for="gender">Gender:</label>
        <select id="gender" v-model="form.gender" required>
          <option value="">Select gender</option>
          <option value="M">Male</option>
          <option value="F">Female</option>
        </select>
      </div>
      
      <div class="form-group">
        <label>
          <input 
            v-model="form.is_committee" 
            type="checkbox"
          />
          Committee Member
        </label>
      </div>
      
      <button type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? 'Adding...' : 'Add Member' }}
      </button>
    </form>
    
    <div v-if="message" :class="messageClass">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const emit = defineEmits(['memberAdded'])

const form = reactive({
  name: '',
  gender: '',
  is_committee: false
})

const isSubmitting = ref(false)
const message = ref('')
const messageClass = ref('')

const submitMember = async () => {
  if (!form.name.trim() || !form.gender) {
    message.value = 'Please fill in all required fields'
    messageClass.value = 'error'
    return
  }
  
  isSubmitting.value = true
  message.value = ''
  
  try {
    const response = await fetch('/members/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(form)
    })
    
    if (response.ok) {
      const newMember = await response.json()
      message.value = `Member "${newMember.name}" added successfully!`
      messageClass.value = 'success'
      
      // Reset form
      form.name = ''
      form.gender = ''
      form.is_committee = false
      
      // Emit event to parent
      emit('memberAdded', newMember)
    } else {
      const error = await response.json()
      message.value = `Error: ${error.detail || 'Failed to add member'}`
      messageClass.value = 'error'
    }
  } catch (error) {
    message.value = 'Network error: Failed to add member'
    messageClass.value = 'error'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.member-form {
  max-width: 400px;
  margin: 20px 0;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input, select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

input[type="checkbox"] {
  width: auto;
  margin-right: 8px;
}

button {
  background-color: #007bff;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover:not(:disabled) {
  background-color: #0056b3;
}

button:disabled {
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
</style>