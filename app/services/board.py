from typing import Optional

from ..objects import Board, Thread
from .database import DatabaseService


class BoardService:
    @classmethod
    async def getBoard(cls, id: str) -> Optional[Board]:
        row = await DatabaseService.pool.fetchrow(
            "SELECT * FROM boards WHERE id = $1", id
        )
        if not row:
            return None
        return Board.model_validate(dict(row))

    @classmethod
    async def write(
        cls,
        board: str,
        *,
        timestamp: int,
        title: str,
        name: str,
        account_id: str,
        content: str
    ) -> Thread:
        row = await DatabaseService.pool.fetchrow(
            "INSERT INTO threads (id, board, title, name, account_id, content) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *",
            timestamp,
            board,
            title,
            name,
            account_id,
            content,
        )
        return Thread.model_validate(dict(row))
