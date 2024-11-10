from fastapi import APIRouter, HTTPException

from ....services.board import BoardService
from ....services.thread import ThreadService

router = APIRouter()


@router.get("/api/boards/{boardName:str}/threads")
async def threadsList(boardName: str, all: bool = False):
    """
    スレッドの一覧をJSONで返します。
    allをtrueにすると全部返しますが、allがfalseの場合は50スレまでしか返ってきません
    """

    board = await BoardService.getBoard(boardName)
    if not board:
        raise HTTPException(status_code=404)
    threads = await ThreadService.getThreads(board.id)
    return threads if all else threads[0:50]
