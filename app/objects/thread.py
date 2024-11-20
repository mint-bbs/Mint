from datetime import datetime

from pydantic import BaseModel, Field


def convertDatetime(dt: datetime) -> str:
    return dt.isoformat()


class Thread(BaseModel):
    id: str
    timestamp: int
    board: str
    title: str
    name: str
    account_id: str
    created_at: datetime
    content: str
    count: int = Field(1)

    class Config:
        json_encoders = {datetime: convertDatetime}
