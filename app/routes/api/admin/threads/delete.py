import os

import bcrypt
import dotenv
from fastapi import APIRouter, Depends, HTTPException

from .....objects import Board
from .....services.admin import AdminPanelSessionService
from .....services.database import DatabaseService
from .....services.thread import ThreadService

dotenv.load_dotenv()

router = APIRouter()


@router.delete("/api/admin/threads/{threadId:str}")
async def deleteThread(
    threadId: str, session: dict = Depends(AdminPanelSessionService.sessionCheck)
):
    """スレッドを削除します。"""
    if not ThreadService.getThreadMON(threadId):
        raise HTTPException(404)
    await DatabaseService.pool.execute("DELETE FROM threads WHERE id = $1", threadId)
    await DatabaseService.pool.execute(
        "DELETE FROM responses WHERE thread_id = $1",
        threadId,
    )
    return {"detail": "success"}
