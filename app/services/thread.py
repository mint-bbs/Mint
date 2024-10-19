import random
import string
from typing import List, Optional

from ..objects import Response, Thread
from .database import DatabaseService


class ThreadService:
    @classmethod
    async def getThread(cls, board: str, threadId: int) -> Optional[Thread]:
        """スレッドを取得します。

        Args:
            board (str): 板のID。
            threadId (str): スレッドのID。

        Returns:
            Optional[Thread]: スレッド一覧
        """
        row = await DatabaseService.pool.fetchrow(
            "SELECT * FROM threads WHERE board = $1 AND id = $2", board, threadId
        )
        if not row:
            return None
        return Thread.model_validate(dict(row))

    @classmethod
    async def getThreads(cls, board: str) -> Optional[List[Thread]]:
        """スレッドの一覧を取得します。

        Args:
            board (str): 板のID。

        Returns:
            Optional[List[Thread]]: スレッド一覧
        """
        rows = await DatabaseService.pool.fetch(
            "SELECT * FROM threads WHERE board = $1 ORDER BY created_at DESC", board
        )
        if not rows:
            return []
        threads = []
        for row in rows:
            threads.append(Thread.model_validate(dict(row)))
        return threads

    @classmethod
    def randomID(cls, n: int = 9) -> str:
        return "".join(random.choices(string.ascii_letters + string.digits, k=n))

    @classmethod
    async def write(
        cls, board: str, threadId: int, *, name: str, account_id: str, content: str
    ) -> Response:
        row = await DatabaseService.pool.fetchrow(
            "INSERT INTO responses (id, thread_id, board, name, account_id, content) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *",
            cls.randomID(10),
            threadId,
            board,
            name,
            account_id,
            content,
        )
        print(row)
        return Response.model_validate(dict(row))
