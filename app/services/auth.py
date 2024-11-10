import secrets
import random
import string
from typing import Optional, Tuple

import orjson
from httpx import AsyncClient

from ..objects import CaptchaType
from .database import DatabaseService
from .meta import MetaDataService


class AuthService:
    @classmethod
    def randomID(cls, n: int = 9) -> str:
        return "".join(random.choices(string.ascii_letters + string.digits, k=n))

    @classmethod
    async def authorize(cls, token: str, ipaddr: str) -> Optional[Tuple[str, str]]:
        client = AsyncClient()

        match MetaDataService.metadata.captcha_type:
            case CaptchaType.TURNSTILE:
                response = await client.post(
                    "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                    headers={"Content-Type": "application/json"},
                    data=orjson.dumps(
                        {
                            "secret": MetaDataService.metadata.captcha_secret,
                            "response": token,
                            "remoteip": ipaddr,
                        }
                    ).decode(),
                )
                jsonData = response.json()
                print(response.status_code, jsonData)
                if not jsonData["success"]:
                    return None
            case CaptchaType.HCAPTCHA:
                response = await client.post(
                    "https://api.hcaptcha.com/siteverify",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "secret": MetaDataService.metadata.captcha_secret,
                        "response": token,
                        "remoteip": ipaddr,
                    },
                )
                jsonData = response.json()
                print(response.status_code, jsonData)
                if not jsonData["success"]:
                    return None
            case CaptchaType.RECAPTCHA:
                response = await client.post(
                    "https://www.google.com/recaptcha/api/siteverify",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "secret": MetaDataService.metadata.captcha_secret,
                        "response": token,
                        "remoteip": ipaddr,
                    },
                )
                jsonData = response.json()
                print(response.status_code, jsonData)
                if not jsonData["success"]:
                    return None

        code = secrets.token_hex(10)
        account_id = cls.randomID(4)

        await DatabaseService.pool.execute(
            """
            INSERT INTO auth(id, account_id) VALUES($1, $2)
        """,
            code,
            account_id,
        )
        return (
            code,
            account_id,
        )

    @classmethod
    async def authCheck(cls, code: str) -> Optional[dict]:
        row = await DatabaseService.pool.fetchrow(
            """
            SELECT * FROM auth WHERE id = $1
        """,
            code,
        )
        return dict(row) if row is not None else None
