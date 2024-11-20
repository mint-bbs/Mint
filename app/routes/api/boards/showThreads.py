from fastapi import APIRouter, HTTPException

from ....services.board import BoardService
from ....services.thread import ThreadService

router = APIRouter()


@router.get("/api/boards/{boardName:str}/threads")
async def threadsList(boardName: str, limit: int = 50):
    """
    スレッドの一覧をJSONで返します。
    """

    board = await BoardService.getBoard(boardName)
    if not board:
        raise HTTPException(status_code=404)
    threads = await ThreadService.getThreads(board.id, limit=limit)
    return threads
