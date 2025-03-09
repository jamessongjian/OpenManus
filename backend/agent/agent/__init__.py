from app.agent.base import BaseAgent
from app.agent.planning import PlanningAgent
from app.agent.react import ReActAgent
from app.agent.swe import SWEAgent
from app.agent.toolcall import ToolCallAgent
from typing import Callable, Optional, Any
import asyncio
from app.config import Config


__all__ = [
    "BaseAgent",
    "PlanningAgent",
    "ReActAgent",
    "SWEAgent",
    "ToolCallAgent",
]

class Agent:
    def __init__(self, config: Config):
        self.config = config
        self.log_callback: Optional[Callable[[str], Any]] = None
        self.browser_callback: Optional[Callable[[str], Any]] = None

    def set_callbacks(self, log_callback: Optional[Callable[[str], Any]] = None,
                     browser_callback: Optional[Callable[[str], Any]] = None):
        """设置回调函数"""
        self.log_callback = log_callback
        self.browser_callback = browser_callback

    async def _log(self, message: str):
        """记录日志"""
        if self.log_callback:
            await self.log_callback(message)

    async def _update_browser(self, content: str):
        """更新浏览器内容"""
        if self.browser_callback:
            await self.browser_callback(content)

    async def run(self, prompt: str) -> dict:
        """运行agent"""
        try:
            # 记录开始执行
            await self._log(f"开始执行指令: {prompt}")

            # TODO: 在这里实现具体的agent逻辑
            # 示例：模拟一些操作
            await self._log("正在分析指令...")
            await asyncio.sleep(1)

            await self._log("开始执行操作...")
            await self._update_browser("<div>正在浏览网页...</div>")
            await asyncio.sleep(1)

            await self._log("操作完成")
            await self._update_browser("<div>任务已完成</div>")

            return {"status": "success", "message": "执行完成"}

        except Exception as e:
            await self._log(f"执行出错: {str(e)}")
            raise
