import bcrypt
import dotenv
from fastapi import APIRouter, Depends, HTTPException

from ....services.admin import AdminPanelSessionService
from ....services.database import DatabaseService

dotenv.load_dotenv()

router = APIRouter()


@router.get("/api/admin/me")
async def me(
    session: dict = Depends(AdminPanelSessionService.sessionCheck),
):
    return session
