import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://doctorj.com.cn:8090',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      },
      '/ws': {
        target: 'ws://doctorj.com.cn:8090',
        ws: true
      }
    }
  }
}) 