<template>
  <div>
    <h2>Schedule</h2>
    <table v-if="schedule.dates">
      <thead>
        <tr><th>Date</th><th>Members</th></tr>
      </thead>
      <tbody>
        <tr v-for="(members, date) in schedule.dates" :key="date">
          <td>{{ date }}</td>
          <td>{{ members.join(', ') }}</td>
        </tr>
      </tbody>
    </table>

    <h3>Statistics</h3>
    <div v-if="schedule.assign_count">
      <h4>Assignment Count</h4>
      <ul>
        <li v-for="(count, member) in schedule.assign_count" :key="member">
          {{ member }}: {{ count }}
        </li>
      </ul>
    </div>
    <div v-if="schedule.committee_count !== undefined">
      <p>Committee Members: {{ schedule.committee_count }}</p>
    </div>
    <div v-if="schedule.gender_count">
      <p>Male: {{ schedule.gender_count.male }} / Female: {{ schedule.gender_count.female }}</p>
    </div>
    <div v-if="schedule.unapplied_rules && schedule.unapplied_rules.length">
      <h4>Unapplied Rules</h4>
      <ul>
        <li v-for="rule in schedule.unapplied_rules" :key="rule">{{ rule }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const schedule = ref({})

const loadSchedule = async () => {
  const res = await fetch('/schedules/latest')
  if (res.ok) {
    schedule.value = await res.json()
  }
}

const refreshSchedule = () => {
  loadSchedule()
}

onMounted(() => {
  loadSchedule()
})

defineExpose({
  refreshSchedule
})
</script>
