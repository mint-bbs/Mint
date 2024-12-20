from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .captchaType import CaptchaType


class ChangeableMetaData(BaseModel):
    id: int
    name: Optional[str] = None
    captcha_type: Optional[CaptchaType] = None
    captcha_sitekey: Optional[str] = None
    captcha_secret: Optional[str] = None


class PublicMetaData(BaseModel):
    id: int
    name: Optional[str] = None
    captcha_type: Optional[CaptchaType] = None
    captcha_sitekey: Optional[str] = None


def convertDatetime(dt: datetime) -> str:
    return dt.isoformat()


class MetaData(BaseModel):
    id: int
    created_at: datetime
    name: str
    captcha_type: CaptchaType
    captcha_sitekey: Optional[str] = None
    captcha_secret: Optional[str] = None

    def public(self):
        return PublicMetaData.model_validate(self.model_dump())

    class Config:
        json_encoders = {datetime: convertDatetime}
