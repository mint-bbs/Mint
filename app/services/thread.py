import asyncio
import secrets
from datetime import datetime
from typing import List, Optional

import orjson

from ..objects import Response, Thread
from .database import DatabaseService


class ThreadService:
    @classmethod
    async def getThreadMON(cls, threadId: str) -> Optional[Thread]:
        """スレッドを取得します。

        Args:
            board (str): 板のID。
            threadId (str): スレッドのID。

        Returns:
            Optional[Thread]: スレッド一覧
        """
        row = await DatabaseService.pool.fetchrow(
            "SELECT * FROM threads WHERE id = $1", threadId
        )
        if not row:
            return None
        return Thread.model_validate(dict(row))

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
            "SELECT * FROM threads WHERE board = $1 AND timestamp = $2", board, threadId
        )
        if not row:
            return None
        return Thread.model_validate(dict(row))

    @classmethod
    async def getThreads(
        cls, board: str, *, offset: int = 0, limit: int = 50, json: bool = False
    ) -> Optional[List[Thread] | str]:
        """スレッドの一覧を取得します。

        Args:
            board (str): 板のID。
            offset (int): オフセット。
            limit (int): 何スレまで取得するか。
            json (bool): スレッドをJSONとして取得するかどうか。

        Returns:
            Optional[List[Thread]]: スレッド一覧
        """
        rows = await DatabaseService.pool.fetch(
            "SELECT * FROM threads WHERE board = $1 ORDER BY last_wrote_at DESC LIMIT $2 OFFSET $3",
            board,
            limit,
            offset,
        )
        if not rows:
            return []
        threads = []
        for row in rows:
            threads.append(
                Thread.model_validate(dict(row))
                if not json
                else Thread.model_validate(dict(row)).model_dump()
            )
        return threads if not json else orjson.dumps(threads).decode()

    @classmethod
    def randomID(cls, n: int = 9) -> str:
        return secrets.token_hex(n)

    @classmethod
    async def write(
        cls,
        board: str,
        threadId: str,
        *,
        name: str,
        account_id: str,
        content: str,
        count: int
    ) -> Response:
        row = await DatabaseService.pool.fetchrow(
            "INSERT INTO responses (id, thread_id, board, name, account_id, content) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *",
            cls.randomID(5),
            threadId,
            board,
            name,
            account_id,
            content,
        )

        asyncio.create_task(
            DatabaseService.pool.execute(
                "UPDATE ONLY threads SET last_wrote_at = $2, count = $3 WHERE id = $1",
                threadId,
                datetime.now(),
                count,
            )
        )

        return Response.model_validate(dict(row))
