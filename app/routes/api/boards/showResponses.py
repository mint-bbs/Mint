from fastapi import APIRouter, HTTPException

from ....objects import Board
from ....services.board import BoardService
from ....services.response import ResponseService
from ....services.thread import ThreadService

router = APIRouter()


@router.get("/api/boards/{boardName:str}/threads/{threadId:int}")
async def threadsList(boardName: str, threadId: int):
    """
    レスの一覧をJSONで返します。
    """

    board = await BoardService.getBoard(boardName)
    if not board:
        raise HTTPException(status_code=404)
    thread = await ThreadService.getThread(board.id, threadId)
    if not thread:
        raise HTTPException(status_code=404)
    responses = await ResponseService.getResponses(thread.id)
    responses.insert(0, thread)
    return responses
