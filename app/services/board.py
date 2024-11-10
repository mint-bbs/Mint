import secrets
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
    def randomID(cls, n: int = 9) -> str:
        return secrets.token_hex(n)

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
        check = await DatabaseService.pool.fetchrow(
            "SELECT * FROM threads WHERE timestamp = $1 AND board = $2",
            timestamp,
            board,
        )

        if check:
            timestamp += 1

        row = await DatabaseService.pool.fetchrow(
            "INSERT INTO threads (id, timestamp, board, title, name, account_id, content) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *",
            cls.randomID(5),
            timestamp,
            board,
            title,
            name,
            account_id,
            content,
        )
        return Thread.model_validate(dict(row))
