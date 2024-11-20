import bcrypt
import dotenv
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

from ....services.admin import AdminPanelSessionService
from ....services.database import DatabaseService

dotenv.load_dotenv()

router = APIRouter()


class LoginUserModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=16)
    password: str


@router.post("/api/admin/login")
async def requestAdminAccount(response: Response, model: LoginUserModel):
    user = await DatabaseService.pool.fetchrow(
        "SELECT * FROM admin_panel_users WHERE username = $1", model.username
    )
    if not user:
        raise HTTPException(status_code=403)
    if not bcrypt.checkpw(model.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=403)
    session_id = await AdminPanelSessionService.login(model.username)

    response.set_cookie("session", session_id, max_age=60 * 60 * 60 * 24 * 365 * 10)
    return {
        "detail": "success",
        "session": session_id,
    }
