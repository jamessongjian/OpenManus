import sys
from pathlib import Path
import logging
import asyncio

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent.parent.parent)
sys.path.append(project_root)

from config.config import AppConfig as Config
from typing import Optional, Callable, Any
from app.agent.manus import Manus
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

class Agent:
    def __init__(self, config: Config):
        self.config = config
        self.log_callback: Optional[Callable[[str], Any]] = None
        self.browser_callback: Optional[Callable[[str], Any]] = None
        self.manus = Manus()  # 创建Manus实例
        self.log_handler = None

    def set_callbacks(
        self,
        log_callback: Optional[Callable[[str], Any]] = None,
        browser_callback: Optional[Callable[[str], Any]] = None
    ):
        self.log_callback = log_callback
        self.browser_callback = browser_callback
        
        # 如果有log_callback，设置日志处理器
        if log_callback:
            if self.log_handler:
                logger.removeHandler(self.log_handler)
            self.log_handler = WebSocketLogHandler(log_callback)
            self.log_handler.setFormatter(logging.Formatter('%(message)s'))
            logger.addHandler(self.log_handler)

    async def run(self, prompt: str) -> str:
        if self.log_callback:
            await self.log_callback({
                "type": "log",
                "message": f"收到提示: {prompt}",
                "level": "INFO"
            })
        
        try:
            # 使用Manus agent执行prompt
            logger.warning("开始处理请求...")
            result = await self.manus.run(prompt)
            
            # 移除日志处理器
            if self.log_handler:
                logger.removeHandler(self.log_handler)
                self.log_handler = None
                
            return "执行完成"
        except Exception as e:
            logger.error(f"执行出错: {str(e)}")
            
            # 移除日志处理器
            if self.log_handler:
                logger.removeHandler(self.log_handler)
                self.log_handler = None
                
            return f"执行出错: {str(e)}"
        finally:
            if self.browser_callback:
                await self.browser_callback("Agent执行完成") 