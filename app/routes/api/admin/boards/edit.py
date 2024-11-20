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


@router.post("/api/admin/boards/{boardId:str}")
async def editBoard(
    boardId: str,
    board: Board,
    session: dict = Depends(AdminPanelSessionService.sessionCheck),
):
    """板を作成します。"""
    if not await BoardService.getBoard(boardId):
        raise HTTPException(status_code=404)
    if board.id != boardId:
        raise HTTPException(status_code=500, detail="Board ID is not changeable")
    await DatabaseService.pool.execute(
        "UPDATE ONLY boards SET name = $2, anonymous_name = $3, deleted_name = $4, subject_count = $5, name_count = $6, message_count = $7, head = $8 WHERE id = $1",
        *board.model_dump().values()
    )
    return board
