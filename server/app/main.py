from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import json
import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from config.config import AppConfig as Config
from app.agent.manus import Manus  # 从项目根目录的app导入
from app.logger import logger

class WebSocketLogHandler(logging.Handler):
    """自定义日志处理器，将日志转发到WebSocket"""
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        
    def emit(self, record):
        try:
            msg = self.format(record)
            asyncio.create_task(self.callback({
                "type": "log",
                "message": msg,
                "level": record.levelname
            }))
        except Exception:
            self.handleError(record)

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
    # 创建日志处理器
    log_handler = WebSocketLogHandler(broadcast_message)
    log_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(log_handler)
    
    try:
        # 创建agent实例
        config = Config()
        agent = Manus()  # 直接使用Manus
        
        # 发送开始执行的消息
        await broadcast_message({
            "type": "log",
            "message": f"收到提示: {request.prompt}",
            "level": "INFO"
        })
        
        # 异步执行agent
        logger.info("开始处理请求...")
        result = await agent.run(request.prompt)
        
        # 发送执行完成的消息
        await broadcast_message({
            "type": "log",
            "message": "执行完成",
            "level": "SUCCESS"
        })
        
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"执行出错: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        # 移除日志处理器
        logger.removeHandler(log_handler)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 