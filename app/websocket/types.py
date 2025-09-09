from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class WebSocketMessage(BaseModel):
    type: str                 # 消息类型，比如 "production_data" | "message" | "system_status"
    timestamp: datetime       # ISO 时间戳，自动解析为 datetime 对象
    data: Any                 # 可以放任意数据，比如 ProductionLineData