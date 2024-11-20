from datetime import datetime

from pydantic import BaseModel


def convertDatetime(dt: datetime) -> str:
    return dt.isoformat()


class Response(BaseModel):
    id: str
    thread_id: str
    board: str
    name: str
    account_id: str
    created_at: datetime
    content: str

    class Config:
        json_encoders = {datetime: convertDatetime}
