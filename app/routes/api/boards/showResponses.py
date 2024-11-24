from fastapi import APIRouter, HTTPException, Request

from ....events import ResponsesRequestEvent
from ....objects import Board
from ....plugin_manager import PluginManager
from ....services.board import BoardService
from ....services.response import ResponseService
from ....services.thread import ThreadService

router = APIRouter()


@router.get("/api/boards/{boardName:str}/threads/{threadId:int}")
async def threadsList(request: Request, boardName: str, threadId: int):
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

    event = ResponsesRequestEvent(request=request, thread=thread, responses=responses)
    for plugin in PluginManager.plugins:
        if getattr(plugin.pluginClass, "onResponsesRequest", None):
            await plugin.pluginClass.onResponsesRequest(event)
            if event.isCancelled():
                raise HTTPException(status_code=3939, detail=event.getCancelMessage())
            thread = event.thread
            responses = event.responses

    responses.insert(0, thread)
    return responses
