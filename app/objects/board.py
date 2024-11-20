from typing import Optional

from pydantic import BaseModel, Field


class Board(BaseModel):
    id: str
    name: str
    anonymous_name: str = Field("名無しさん")
    deleted_name: str = Field("あぼーん")
    subject_count: int = Field(64)
    name_count: int = Field(50)
    message_count: int = Field(2000)
    head: str = Field(
        '<div style="text-align: center; margin: 1.2em 0">\n    <span style="color: red">クリックで救える命が…ないです(｀･ω･´)ｼｬｷｰﾝ</span>\n</div>\n\n<b>掲示板使用上の注意</b>\n<ul style="font-weight:bold;">\n    <li>･転んでも泣かない</li>\n    <li>･出されたものは残さず食べる</li>\n    <li>･Python使いを尊重する</li>\n</ul>'
    )
