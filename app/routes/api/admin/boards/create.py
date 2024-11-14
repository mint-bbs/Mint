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


@router.put("/api/admin/boards")
async def createBoard(
    board: Board, session: dict = Depends(AdminPanelSessionService.sessionCheck)
):
    """板を作成します。"""
    if not board.id.isalnum():
        raise HTTPException(status_code=500, detail="That board ID is not available.")

    if (board.id == "auth") or (board.id == "bbsmenu.html") or (board.id == "admin"):
        raise HTTPException(status_code=500, detail="That board ID is not available.")
    if await BoardService.getBoard(board.id):
        raise HTTPException(status_code=500, detail="Board ID already used")
    await DatabaseService.pool.execute(
        "INSERT INTO boards (id, name, anonymous_name, deleted_name, subject_count, name_count, message_count, head) values ($1, $2, $3, $4, $5, $6, $7, $8)",
        *board.model_dump().values()
    )
    return board
