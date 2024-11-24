from fastapi import APIRouter, HTTPException, Request

from ....events import ThreadsRequestEvent
from ....plugin_manager import PluginManager
from ....services.board import BoardService
from ....services.thread import ThreadService

router = APIRouter()


@router.get("/api/boards/{boardName:str}/threads")
async def threadsList(request: Request, boardName: str, limit: int = 50):
    """
    スレッドの一覧をJSONで返します。
    """

    board = await BoardService.getBoard(boardName)
    if not board:
        raise HTTPException(status_code=404)
    threads = await ThreadService.getThreads(board.id, limit=limit)

    event = ThreadsRequestEvent(request=request, threads=threads)
    for plugin in PluginManager.plugins:
        if getattr(plugin.pluginClass, "onThreadsRequest", None):
            await plugin.pluginClass.onThreadsRequest(event)
            if event.isCancelled():
                raise HTTPException(status_code=3939, detail=event.getCancelMessage())
            threads = event.threads

    return threads
