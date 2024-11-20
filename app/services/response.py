from typing import List, Optional

from ..objects import Response
from .database import DatabaseService


class ResponseService:
    @classmethod
    async def getResponses(cls, threadId: str) -> Optional[List[Response]]:
        """スレッドについたレスの一覧を返します。

        Args:
            board (str): 板のID。
            thread_id (int): スレッドのID。

        Returns:
            Optional[List[Response]]: レス一覧
        """
        rows = await DatabaseService.pool.fetch(
            "SELECT * FROM responses WHERE thread_id = $1 ORDER BY created_at ASC",
            threadId,
        )
        if not rows:
            return []
        responses = []
        for row in rows:
            responses.append(Response.model_validate(dict(row)))
        return responses
