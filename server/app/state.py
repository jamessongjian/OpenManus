from fastapi import WebSocket
from app.logger import logger

# 存储客户端的WebSocket连接
clients = set()

async def broadcast_message(message: str):
    """
    向所有连接的客户端广播消息
    
    Args:
        message (str): 要广播的消息
    """
    logger.info(f"准备广播消息给 {len(clients)} 个客户端")
    disconnected_clients = set()
    
    for client_ws in clients:
        try:
            await client_ws.send_text(message)
            logger.debug("消息发送成功")
        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}")
            disconnected_clients.add(client_ws)
    
    # 移除断开连接的客户端
    for client in disconnected_clients:
        clients.remove(client) 