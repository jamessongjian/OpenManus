<template>
  <div class="min-h-screen bg-gray-50">
    <div class="container mx-auto px-4 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 左侧面板 -->
        <div class="space-y-6">
          <!-- 日志区域 -->
          <div class="bg-white rounded-xl shadow-lg p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-xl font-semibold text-gray-800">执行日志</h2>
              <el-tag :type="wsStatus === 'connected' ? 'success' : 'warning'" size="small">
                {{ wsStatus === 'connected' ? '已连接' : '未连接' }}
              </el-tag>
            </div>
            <div ref="logAreaRef" class="h-[40vh] overflow-y-auto font-mono text-sm text-gray-600 whitespace-pre-wrap p-4 bg-gray-50 rounded-lg">
              <div v-for="(log, index) in logs" :key="index" class="py-1" :class="{'text-red-500': log.type === 'error'}">
                {{ log.message }}
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="bg-white rounded-xl shadow-lg p-6">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">输入指令</h2>
            <el-input
              v-model="userInput"
              type="textarea"
              :rows="6"
              placeholder="请输入您的指令..."
              resize="none"
              class="mb-4"
            />
            <el-button
              type="primary"
              :loading="isExecuting"
              @click="executeCommand"
              class="w-full"
            >
              {{ isExecuting ? '执行中...' : '执行指令' }}
            </el-button>
          </div>
        </div>

        <!-- 右侧浏览器区域 -->
        <div class="bg-white rounded-xl shadow-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold text-gray-800">浏览器操作</h2>
            <div class="flex gap-2">
              <div class="h-3 w-3 rounded-full" :class="[
                wsStatus === 'connected' ? 'bg-green-400' : 'bg-red-400'
              ]"></div>
            </div>
          </div>
          <div class="h-[calc(100vh-10rem)] bg-gray-50 rounded-lg border border-gray-200 p-4 overflow-y-auto">
            <div v-html="browserContent"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

const userInput = ref('')
const logs = ref([])
const browserContent = ref('')
const isExecuting = ref(false)
const wsStatus = ref('disconnected')
let ws = null

const logAreaRef = ref(null)

// 滚动到日志底部
const scrollToBottom = () => {
  if (logAreaRef.value) {
    logAreaRef.value.scrollTop = logAreaRef.value.scrollHeight
  }
}

// 添加日志
const addLog = (message, type = 'info') => {
  logs.value.push({ message, type })
  setTimeout(scrollToBottom, 50)
}

// 连接 WebSocket
const connectWebSocket = () => {
  ws = new WebSocket('ws://doctorj.com.cn:8090/ws')

  ws.onopen = () => {
    wsStatus.value = 'connected'
    addLog('WebSocket 连接已建立')
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'log') {
        addLog(data.message)
      } else if (data.type === 'browser') {
        browserContent.value = data.content
      }
    } catch (error) {
      addLog('解析消息失败: ' + error.message, 'error')
    }
  }

  ws.onclose = () => {
    wsStatus.value = 'disconnected'
    addLog('WebSocket 连接已断开', 'error')
    setTimeout(connectWebSocket, 5000) // 5秒后重连
  }

  ws.onerror = (error) => {
    addLog('WebSocket 错误: ' + error.message, 'error')
  }
}

// 执行命令
const executeCommand = async () => {
  if (!userInput.value.trim()) {
    ElMessage.warning('请输入指令')
    return
  }

  try {
    isExecuting.value = true
    const response = await fetch('http://doctorj.com.cn:8090/api/execute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt: userInput.value })
    })

    if (!response.ok) {
      throw new Error('请求失败')
    }

    userInput.value = ''
    ElMessage.success('指令已发送')
  } catch (error) {
    addLog('执行指令失败: ' + error.message, 'error')
    ElMessage.error('执行失败')
  } finally {
    isExecuting.value = false
  }
}

// 生命周期钩子
onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
})
</script>

<style>
.el-input__wrapper {
  box-shadow: none !important;
}
</style> 