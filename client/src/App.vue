<template>
  <div class="min-h-screen bg-gray-900 text-gray-100">
    <div class="container mx-auto px-4 py-6">
      <!-- 顶部标题栏 -->
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center space-x-3">
          <div class="text-2xl font-bold text-white">
            OpenManus Agent
          </div>
          <el-tag 
            :type="wsStatus === 'connected' ? 'success' : 'warning'" 
            size="small"
            class="border-none"
          >
            {{ wsStatus === 'connected' ? '已连接' : '未连接' }}
          </el-tag>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 左侧面板 -->
        <div class="space-y-6">
          <!-- 日志区域 -->
          <div class="bg-gray-800 rounded-lg border border-gray-700">
            <div class="p-4 border-b border-gray-700">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-2">
                  <div class="h-2 w-2 rounded-full bg-emerald-400"></div>
                  <h2 class="text-lg font-medium">执行步骤</h2>
                </div>
                <el-button-group>
                  <el-button size="small" type="info" text @click="clearLogs">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                  <el-button size="small" type="info" text @click="downloadLogs">
                    <el-icon><Download /></el-icon>
                  </el-button>
                </el-button-group>
              </div>
            </div>
            <div 
              ref="logAreaRef" 
              class="h-[40vh] overflow-y-auto font-mono text-sm p-4 space-y-1 custom-scrollbar"
            >
              <div 
                v-for="(log, index) in logs" 
                :key="index" 
                class="py-1 px-2 rounded flex items-start space-x-2"
                :class="{
                  'text-red-400 bg-red-900/20': log.type === 'error',
                  'text-gray-300': log.type === 'info',
                  'text-yellow-400': log.type === 'warning',
                  'text-green-400': log.type === 'success'
                }"
              >
                <span class="inline-block w-5 text-right">{{ index + 1 }}.</span>
                <span class="flex-1">{{ log.message }}</span>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-medium">输入指令</h2>
              <el-dropdown trigger="click">
                <el-button size="small" type="info" text>
                  <el-icon><More /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item>清空输入</el-dropdown-item>
                    <el-dropdown-item>保存模板</el-dropdown-item>
                    <el-dropdown-item>载入模板</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
            <el-input
              v-model="userInput"
              type="textarea"
              :rows="6"
              placeholder="请输入您的指令..."
              resize="none"
              class="mb-4 custom-input"
            />
            <div class="flex space-x-3">
              <el-button
                type="primary"
                :loading="isExecuting"
                @click="executeCommand"
                class="flex-1"
              >
                <template #icon>
                  <el-icon><VideoPlay /></el-icon>
                </template>
                {{ isExecuting ? '执行中...' : '执行指令' }}
              </el-button>
              <el-button type="info" text>
                <el-icon><RefreshRight /></el-icon>
              </el-button>
            </div>
          </div>
        </div>

        <!-- 右侧浏览器区域 -->
        <div class="bg-gray-800 rounded-lg border border-gray-700">
          <div class="p-4 border-b border-gray-700">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-medium">浏览器操作</h2>
              <div class="flex space-x-2">
                <div class="h-2 w-2 rounded-full bg-red-400"></div>
                <div class="h-2 w-2 rounded-full bg-yellow-400"></div>
                <div class="h-2 w-2 rounded-full bg-emerald-400"></div>
              </div>
            </div>
          </div>
          <div class="h-[calc(100vh-12rem)] p-4">
            <div 
              class="h-full bg-gray-900 rounded border border-gray-700 p-4 overflow-y-auto custom-scrollbar"
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
import { ElMessage } from 'element-plus'
import { Delete, Download, More, VideoPlay, RefreshRight } from '@element-plus/icons-vue'

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
    ElMessage.warning('请输入指令')
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
    ElMessage.success('指令已发送')
  } catch (error) {
    console.error('执行命令错误:', error)
    addLog(`执行失败: ${error.message}`, 'error')
    ElMessage.error(`执行失败: ${error.message}`)
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
        // 根据消息内容设置不同的类型
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
  background: rgba(31, 41, 55, 0.5);
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(75, 85, 99, 0.5);
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(107, 114, 128, 0.5);
}

.custom-input .el-textarea__inner {
  background: rgba(17, 24, 39, 0.3) !important;
  border-color: rgba(75, 85, 99, 0.5) !important;
  color: #e5e7eb !important;
}

.custom-input .el-textarea__inner:focus {
  border-color: #3b82f6 !important;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1) !important;
}

.el-button--primary {
  background-color: #3b82f6 !important;
  border-color: #3b82f6 !important;
}

.el-button--primary:hover {
  background-color: #2563eb !important;
  border-color: #2563eb !important;
}

.el-message {
  background: #1f2937 !important;
  border: 1px solid #374151 !important;
  color: #e5e7eb !important;
}

.el-message--success .el-message__icon {
  color: #10b981 !important;
}

.el-message--warning .el-message__icon {
  color: #f59e0b !important;
}

.el-message--error .el-message__icon {
  color: #ef4444 !important;
}

.el-dropdown-menu {
  background: #1f2937 !important;
  border: 1px solid #374151 !important;
}

.el-dropdown-menu__item {
  color: #e5e7eb !important;
}

.el-dropdown-menu__item:hover {
  background: #374151 !important;
}
</style> 