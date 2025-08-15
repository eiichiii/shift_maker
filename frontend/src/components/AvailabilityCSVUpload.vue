<template>
  <div class="availability-csv-upload">
    <h3>Upload Availability from CSV</h3>
    
    <div class="format-info">
      <h4>CSV Format Requirements:</h4>
      <div class="format-example">
        <pre>,nameA,nameB,nameC
2025/8/1,×,○,○
2025/8/4,○,○,○
2025/8/30,○,○,×</pre>
      </div>
      <ul class="format-rules">
        <li><strong>Header row</strong>: First column empty, followed by member names</li>
        <li><strong>Data rows</strong>: Date (YYYY/MM/DD format), followed by availability</li>
        <li><strong>Availability symbols</strong>: ○ (available), × (not available)</li>
        <li><strong>Member names</strong>: Must match existing members in the database</li>
      </ul>
    </div>

    <div class="upload-section">
      <div class="file-input-wrapper">
        <input 
          ref="fileInput"
          type="file" 
          accept=".csv"
          @change="handleFileSelect"
          class="file-input"
          id="availability-csv-file-input"
        />
        <label for="availability-csv-file-input" class="file-input-label">
          <span v-if="!selectedFile">Choose CSV File</span>
          <span v-else>{{ selectedFile.name }}</span>
        </label>
      </div>
      
      <button 
        @click="uploadCSV" 
        :disabled="!selectedFile || isUploading"
        class="upload-btn"
      >
        {{ isUploading ? 'Uploading...' : 'Upload CSV' }}
      </button>
    </div>

    <div v-if="uploadResult" class="upload-result">
      <div :class="uploadResult.success ? 'success' : 'error'">
        <h4>{{ uploadResult.success ? 'Upload Successful' : 'Upload Failed' }}</h4>
        <p>{{ uploadResult.message }}</p>
        
        <div v-if="uploadResult.success && uploadResult.data" class="result-summary">
          <div class="summary-stats">
            <div class="stat-item">
              <span class="stat-label">Processed Dates:</span>
              <span class="stat-value">{{ uploadResult.data.processed_dates }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Processed Members:</span>
              <span class="stat-value">{{ uploadResult.data.processed_members }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Total Availabilities:</span>
              <span class="stat-value">{{ uploadResult.data.total_availabilities }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Errors:</span>
              <span class="stat-value error-count">{{ uploadResult.data.error_count }}</span>
            </div>
          </div>
          
          <div v-if="uploadResult.data.errors && uploadResult.data.errors.length > 0" class="error-details">
            <h5>Errors encountered:</h5>
            <ul>
              <li v-for="error in uploadResult.data.errors" :key="error">{{ error }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['uploadCompleted'])

const fileInput = ref()
const selectedFile = ref(null)
const isUploading = ref(false)
const uploadResult = ref(null)

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file && file.type === 'text/csv') {
    selectedFile.value = file
    uploadResult.value = null
  } else {
    selectedFile.value = null
    uploadResult.value = {
      success: false,
      message: 'Please select a valid CSV file'
    }
  }
}

const uploadCSV = async () => {
  if (!selectedFile.value) {
    uploadResult.value = {
      success: false,
      message: 'Please select a CSV file first'
    }
    return
  }

  isUploading.value = true
  uploadResult.value = null

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await fetch('/availabilities/upload-csv', {
      method: 'POST',
      body: formData
    })

    const result = await response.json()

    if (response.ok) {
      uploadResult.value = {
        success: true,
        message: result.message,
        data: result
      }
      
      // Clear the file input
      selectedFile.value = null
      if (fileInput.value) {
        fileInput.value.value = ''
      }
      
      // Emit event to parent to refresh availability data
      emit('uploadCompleted', result)
    } else {
      uploadResult.value = {
        success: false,
        message: result.detail || 'Upload failed'
      }
    }
  } catch (error) {
    uploadResult.value = {
      success: false,
      message: `Network error: ${error.message}`
    }
  } finally {
    isUploading.value = false
  }
}
</script>

<style scoped>
.availability-csv-upload {
  max-width: 700px;
  margin: 20px 0;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #f9f9f9;
}

.format-info {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #e3f2fd;
  border-radius: 5px;
  border-left: 4px solid #2196f3;
}

.format-info h4 {
  margin: 0 0 10px 0;
  color: #1976d2;
}

.format-example {
  margin: 10px 0;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.format-example pre {
  margin: 0;
  font-size: 13px;
}

.format-rules {
  margin: 10px 0 0 0;
  padding-left: 20px;
}

.format-rules li {
  margin-bottom: 5px;
  color: #555;
}

.upload-section {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 20px;
}

.file-input-wrapper {
  position: relative;
  overflow: hidden;
}

.file-input {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.file-input-label {
  display: inline-block;
  padding: 10px 20px;
  background-color: #f8f9fa;
  border: 2px dashed #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 200px;
  text-align: center;
}

.file-input-label:hover {
  background-color: #e9ecef;
  border-color: #adb5bd;
}

.upload-btn {
  background-color: #17a2b8;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.upload-btn:hover:not(:disabled) {
  background-color: #138496;
}

.upload-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.upload-result {
  margin-top: 20px;
}

.success {
  color: #155724;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 4px;
  padding: 15px;
}

.error {
  color: #721c24;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  padding: 15px;
}

.success h4, .error h4 {
  margin: 0 0 10px 0;
}

.result-summary {
  margin-top: 15px;
}

.summary-stats {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 12px;
  background-color: rgba(255,255,255,0.7);
  border-radius: 4px;
  min-width: 120px;
}

.stat-label {
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
}

.stat-value {
  font-weight: bold;
  font-size: 18px;
  margin-top: 2px;
}

.error-count {
  color: #dc3545;
}

.error-details {
  background-color: rgba(255,255,255,0.7);
  padding: 10px;
  border-radius: 4px;
}

.error-details h5 {
  margin: 0 0 10px 0;
  color: #721c24;
}

.error-details ul {
  margin: 0;
  padding-left: 20px;
}

.error-details li {
  margin-bottom: 5px;
  font-size: 14px;
}

@media (max-width: 600px) {
  .upload-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .summary-stats {
    flex-direction: column;
    gap: 10px;
  }
  
  .stat-item {
    flex-direction: row;
    justify-content: space-between;
  }
}
</style>