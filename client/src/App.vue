<template>
  <div class="min-h-screen bg-[#1a1a1a] text-gray-100 p-6">
    <div class="max-w-[1800px] mx-auto">
      <!-- 顶部标题栏 -->
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center space-x-3">
          <div class="text-2xl font-bold text-white">
            OpenManus Agent
          </div>
          <div 
            class="px-2 py-1 text-sm rounded-full" 
            :class="wsStatus === 'connected' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'"
          >
            {{ wsStatus === 'connected' ? '已连接' : '未连接' }}
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 左侧面板 -->
        <div class="space-y-6">
          <!-- 执行步骤区域 -->
          <div class="bg-[#2a2a2a] rounded-xl border border-gray-800">
            <div class="p-4 border-b border-gray-800">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-2">
                  <div class="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
                  <h2 class="text-lg font-medium">执行步骤</h2>
                </div>
                <div class="flex space-x-2">
                  <button 
                    @click="clearLogs" 
                    class="p-1.5 rounded-lg hover:bg-gray-700/50 text-gray-400 hover:text-gray-300 transition-colors"
                  >
                    <Delete class="w-4 h-4" />
                  </button>
                  <button 
                    @click="downloadLogs" 
                    class="p-1.5 rounded-lg hover:bg-gray-700/50 text-gray-400 hover:text-gray-300 transition-colors"
                  >
                    <Download class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
            <div 
              ref="logAreaRef" 
              class="h-[40vh] overflow-y-auto font-mono text-sm p-4 space-y-1.5 custom-scrollbar"
            >
              <div 
                v-for="(log, index) in logs" 
                :key="index" 
                class="py-1.5 px-3 rounded flex items-start space-x-3 transition-colors"
                :class="{
                  'bg-red-500/10 text-red-400': log.type === 'error',
                  'text-gray-300': log.type === 'info',
                  'bg-yellow-500/10 text-yellow-400': log.type === 'warning',
                  'bg-green-500/10 text-green-400': log.type === 'success'
                }"
              >
                <span class="inline-block text-gray-500 font-medium">{{ index + 1 }}.</span>
                <span class="flex-1">{{ log.message }}</span>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="bg-[#2a2a2a] rounded-xl border border-gray-800 p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-medium">输入指令</h2>
              <button 
                class="p-1.5 rounded-lg hover:bg-gray-700/50 text-gray-400 hover:text-gray-300 transition-colors"
                @click="showOptions = !showOptions"
              >
                <More class="w-4 h-4" />
              </button>
            </div>
            <textarea
              v-model="userInput"
              rows="6"
              placeholder="请输入您的指令..."
              class="w-full px-4 py-3 bg-[#1a1a1a] border border-gray-800 rounded-lg text-gray-300 placeholder-gray-600 focus:outline-none focus:border-green-600 focus:ring-1 focus:ring-green-600 transition-colors resize-none mb-4"
            ></textarea>
            <div class="flex space-x-3">
              <button
                @click="executeCommand"
                :disabled="isExecuting"
                class="flex-1 px-6 py-2.5 bg-green-600 hover:bg-green-700 disabled:bg-green-800 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
              >
                <VideoPlay v-if="!isExecuting" class="w-4 h-4" />
                <div v-else class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                <span>{{ isExecuting ? '执行中...' : '执行指令' }}</span>
              </button>
              <button 
                class="p-2.5 rounded-lg hover:bg-gray-700/50 text-gray-400 hover:text-gray-300 transition-colors"
              >
                <RefreshRight class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        <!-- 右侧浏览器区域 -->
        <div class="bg-white rounded-xl border border-gray-200 shadow-sm">
          <div class="p-4 border-b border-gray-100">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-medium text-gray-900">浏览器操作</h2>
              <div class="flex space-x-2">
                <div class="h-2.5 w-2.5 rounded-full bg-red-400"></div>
                <div class="h-2.5 w-2.5 rounded-full bg-yellow-400"></div>
                <div class="h-2.5 w-2.5 rounded-full bg-green-500"></div>
              </div>
            </div>
          </div>
          <div class="h-[calc(100vh-12rem)] p-4">
            <div 
              class="h-full bg-gray-50 rounded-lg border border-gray-200 p-4 overflow-y-auto custom-scrollbar"
              v-html="browserContent"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Delete, Download, More, VideoPlay, RefreshRight } from '@element-plus/icons-vue'

const userInput = ref('')
const logs = ref([])
const browserContent = ref('')
const isExecuting = ref(false)
const wsStatus = ref('disconnected')
const showOptions = ref(false)
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

// 清空日志
const clearLogs = () => {
  logs.value = []
}

// 下载日志
const downloadLogs = () => {
  const logText = logs.value
    .map((log, index) => `${index + 1}. ${log.message}`)
    .join('\n')
  
  const blob = new Blob([logText], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `execution-steps-${new Date().toISOString().slice(0, 19)}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// 执行命令
const executeCommand = async () => {
  if (!userInput.value.trim()) {
    addLog('请输入指令', 'warning')
    return
  }

  try {
    isExecuting.value = true
    addLog('开始执行指令...', 'info')
    
    const response = await fetch('/api/execute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt: userInput.value })
    })

    if (!response.ok) {
      throw new Error(`请求失败: ${response.status}`)
    }

    const result = await response.json()
    addLog(`服务器已接收指令: ${userInput.value}`, 'success')
    console.log('服务器响应:', result)
    
    userInput.value = ''
  } catch (error) {
    console.error('执行命令错误:', error)
    addLog(`执行失败: ${error.message}`, 'error')
  } finally {
    isExecuting.value = false
  }
}

// 连接 WebSocket
const connectWebSocket = () => {
  ws = new WebSocket(`ws://${window.location.host}/ws`)

  ws.onopen = () => {
    wsStatus.value = 'connected'
    addLog('系统已就绪', 'success')
    console.log('WebSocket connected')
  }

  ws.onmessage = (event) => {
    try {
      console.log('收到服务器消息:', event.data)
      const data = JSON.parse(event.data)
      if (data.type === 'log') {
        const type = data.message.toLowerCase().includes('error') ? 'error' 
          : data.message.toLowerCase().includes('warning') ? 'warning'
          : data.message.toLowerCase().includes('success') ? 'success'
          : 'info'
        addLog(data.message, type)
      } else if (data.type === 'browser') {
        browserContent.value = data.content
        addLog('浏览器操作已更新', 'info')
      }
    } catch (error) {
      console.error('解析服务器消息失败:', error)
      addLog(`消息解析失败: ${error.message}`, 'error')
    }
  }

  ws.onclose = () => {
    wsStatus.value = 'disconnected'
    addLog('连接已断开，正在重新连接...', 'warning')
    console.log('WebSocket disconnected, 将在5秒后重连')
    setTimeout(connectWebSocket, 5000)
  }

  ws.onerror = (error) => {
    console.error('WebSocket 错误:', error)
    addLog('连接发生错误', 'error')
  }
}

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
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(75, 85, 99, 0.2);
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(75, 85, 99, 0.3);
}
</style> 