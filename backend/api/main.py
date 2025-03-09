from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import asyncio

from backend.agent.agent.manus import Manus
from backend.agent.logger import logger

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExecuteRequest(BaseModel):
    prompt: str

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = WebSocketManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/execute")
async def execute_command(request: ExecuteRequest):
    try:
        # 创建Agent实例
        agent = Manus()
        
        # 设置回调函数来发送实时日志
        async def log_callback(message: str):
            await manager.broadcast({"type": "log", "message": message})
            
        async def browser_callback(content: str):
            await manager.broadcast({"type": "browser", "content": content})
            
        agent.set_callbacks(log_callback, browser_callback)
        
        # 执行命令
        result = await agent.run(request.prompt)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"执行命令出错: {str(e)}")
        return {"status": "error", "message": str(e)} 