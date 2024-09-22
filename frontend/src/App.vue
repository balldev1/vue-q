<template>
  <div class="max-w-lg mx-auto p-6 bg-white rounded shadow-md">
    <h1 class="text-2xl font-bold mb-4">Queue Management</h1>
    <form @submit.prevent="addQueue">
      <div class="mb-4">
        <label for="truckType" class="block text-sm font-medium text-gray-700">Select Truck Type:</label>
        <select v-model="truckType" id="truckType" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-500">
          <option v-for="truck in truckTypes" :key="truck.id" :value="truck.id">
            {{ truck.name }}
          </option>
        </select>
      </div>

      <div class="mb-4">
        <label for="doorType" class="block text-sm font-medium text-gray-700">Select Door Type:</label>
        <select v-model="doorType" id="doorType" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-500">
          <option v-for="door in doorTypes" :key="door.id" :value="door.id">
            {{ door.number }}
          </option>
        </select>
      </div>

      <button type="submit" class="w-full py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700">Add to Queue</button>
    </form>

    <h2 class="text-xl font-semibold mt-6">Queues</h2>
    <ul class="mt-2">
      <li v-for="queue in queues" :key="queue.id" class="border-b py-2">{{ queue.truck_type }} - {{ queue.door_type }}</li>
    </ul>

    <div v-if="notification" class="mt-4 p-2 bg-green-200 rounded">{{ notification }}</div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      truckType: '',
      doorType: '',
      queues: [],
      truckTypes: [],
      doorTypes: [],
      notification: '',  // ตัวแปรสำหรับเก็บการแจ้งเตือน
    };
  },
  methods: {
    async addQueue() {
      try {
        const payload = {
          truck_type: String(this.truckType),
          door_type: String(this.doorType),
        };

        await axios.post('http://localhost:8000/api/queue/', payload);
        this.loadQueues();
      } catch (error) {
        console.error("Error adding queue:", error);
      }
    },
    async loadQueues() {
      try {
        const response = await axios.get('http://localhost:8000/api/queue/');
        this.queues = response.data;
      } catch (error) {
        console.error("Error loading queues:", error);
      }
    },
    async loadTruckTypes() {
      try {
        const response = await axios.get('http://localhost:8000/api/truck-types/');
        this.truckTypes = response.data;
      } catch (error) {
        console.error("Error loading truck types:", error);
      }
    },
    async loadDoorTypes() {
      try {
        const response = await axios.get('http://localhost:8000/api/door-types/');
        this.doorTypes = response.data;
      } catch (error) {
        console.error("Error loading door types:", error);
      }
    },
    setupWebSocket() {
      const ws = new WebSocket("ws://localhost:8000/ws");
      ws.onmessage = (event) => {
        this.notification = event.data; // แสดงข้อความแจ้งเตือน
      };
    }
  },
  mounted() {
    this.loadTruckTypes();
    this.loadDoorTypes();
    this.loadQueues();
    this.setupWebSocket(); // เรียกใช้ฟังก์ชันตั้งค่า WebSocket
  }
};
</script>

<style scoped>
/* เพิ่มสไตล์เพิ่มเติมที่คุณต้องการ */
</style>
