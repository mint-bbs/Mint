from datetime import datetime

from pydantic import BaseModel


class Response(BaseModel):
    id: str
    thread_id: int
    board: str
    name: str
    account_id: str
    created_at: datetime
    content: str
