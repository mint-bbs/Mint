from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ...services.auth import AuthService

router = APIRouter()


class AuthModel(BaseModel):
    token: str


@router.post("/api/auth")
async def auth(request: Request, body: AuthModel):
    """
    認証します。
    """
    if "X_FORWARDED_FOR" in request.headers:
        ipaddr = request.headers["X_FORWARDED_FOR"]
    else:
        if not request.client or not request.client.host:
            ipaddr = "127.0.0.1"

        ipaddr = request.client.host

    code, account_id = await AuthService.authorize(body.token, ipaddr)
    if (not code) or (not account_id):
        raise HTTPException(status_code=500, detail="failed")
    return {"detail": "success", "code": code, "account_id": account_id}
