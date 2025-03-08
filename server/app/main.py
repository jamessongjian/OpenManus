from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import json
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from config.config import AppConfig as Config
from app.agent import Agent

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

# 存储所有活动的WebSocket连接
active_connections: list[WebSocket] = []

async def broadcast_message(message: dict):
    """向所有连接的客户端广播消息"""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            pass

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # 保持连接活跃
    except:
        active_connections.remove(websocket)

@app.post("/api/execute")
async def execute_prompt(request: PromptRequest):
    # 创建agent实例
    config = Config()
    agent = Agent(config)
    
    # 定义回调函数来处理agent的输出
    async def log_callback(message: str):
        await broadcast_message({
            "type": "log",
            "message": message
        })
    
    async def browser_callback(content: str):
        await broadcast_message({
            "type": "browser",
            "content": content
        })
    
    # 设置agent的回调函数
    agent.set_callbacks(
        log_callback=log_callback,
        browser_callback=browser_callback
    )
    
    # 异步执行agent
    try:
        result = await agent.run(request.prompt)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 