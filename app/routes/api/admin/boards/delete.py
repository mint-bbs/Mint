import os

import bcrypt
import dotenv
from fastapi import APIRouter, Depends, HTTPException

from .....objects import Board
from .....services.admin import AdminPanelSessionService
from .....services.board import BoardService
from .....services.database import DatabaseService

dotenv.load_dotenv()

router = APIRouter()


@router.delete("/api/admin/boards/{boardId:str}")
async def deleteBoard(
    boardId: str, session: dict = Depends(AdminPanelSessionService.sessionCheck)
):
    """スレッドを削除します。"""
    if not BoardService.getBoard(boardId):
        raise HTTPException(404)
    await DatabaseService.pool.execute("DELETE FROM boards WHERE id = $1", boardId)
    await DatabaseService.pool.execute("DELETE FROM threads WHERE board = $1", boardId)
    await DatabaseService.pool.execute(
        "DELETE FROM responses WHERE board = $1",
        boardId,
    )
    return {"detail": "success"}
