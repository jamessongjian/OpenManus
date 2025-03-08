import os
from pathlib import Path
from typing import Dict, Optional
from pydantic import BaseModel, Field

def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).resolve().parent.parent

PROJECT_ROOT = get_project_root()

class ServerConfig(BaseModel):
    """服务器配置"""
    host: str = Field("http://localhost", description="服务器主机地址")
    port: int = Field(8000, description="服务器端口")
    ws_path: str = Field("/ws", description="WebSocket路径")
    api_path: str = Field("/api", description="API路径")

    @property
    def base_url(self) -> str:
        """获取完整的服务器基础URL"""
        return f"{self.host}:{self.port}"
    
    @property
    def ws_url(self) -> str:
        """获取WebSocket完整URL"""
        return f"ws://{self.host.replace('http://', '')}:{self.port}{self.ws_path}"
    
    @property
    def api_url(self) -> str:
        """获取API完整URL"""
        return f"{self.base_url}{self.api_path}"

class AppConfig(BaseModel):
    """应用配置"""
    server: ServerConfig = ServerConfig()
    debug: bool = Field(True, description="是否开启调试模式")
    log_level: str = Field("INFO", description="日志级别")

# 全局配置实例
config = AppConfig()

# 从环境变量更新配置
if os.getenv("SERVER_HOST"):
    config.server.host = os.getenv("SERVER_HOST")
if os.getenv("SERVER_PORT"):
    config.server.port = int(os.getenv("SERVER_PORT"))
if os.getenv("DEBUG"):
    config.debug = os.getenv("DEBUG").lower() == "true"
if os.getenv("LOG_LEVEL"):
    config.log_level = os.getenv("LOG_LEVEL").upper() 