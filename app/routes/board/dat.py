from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse

from ...events import DatRequestEvent
from ...plugin_manager import PluginManager
from ...services.board import BoardService
from ...services.response import ResponseService
from ...services.thread import ThreadService

router = APIRouter()

weekdays = ["月", "火", "水", "木", "金", "土", "日"]


@router.get(
    "/{boardName:str}/dat/{threadId:int}.dat",
    response_class=PlainTextResponse,
)
async def dat(request: Request, boardName: str, threadId: int):
    """
    Monazilla 1.0の形式のスレッドデータ
    """
    board = await BoardService.getBoard(boardName)
    if not board:
        raise HTTPException(status_code=404)
    thread = await ThreadService.getThread(board.id, threadId)
    if not thread:
        raise HTTPException(status_code=404)
    responses = await ResponseService.getResponses(thread.id)
    threadDat = []

    event = DatRequestEvent(request, thread, responses)
    for plugin in PluginManager.plugins:
        if getattr(plugin.pluginClass, "onDatRequest", None):
            await plugin.pluginClass.onDatRequest(event)
            if event.isCancelled():
                raise HTTPException(status_code=439, detail=event.getCancelMessage())
            thread = event.thread
            responses = event.responses

    thread.created_at = thread.created_at.astimezone(ZoneInfo("Asia/Tokyo"))
    thread.content = thread.content.replace("\n", " <br> ")
    threadDat.append(
        f"{thread.name}<><>{thread.created_at.strftime('%Y/%m/%d')}({weekdays[thread.created_at.weekday()]}) {thread.created_at.strftime('%H:%M:%S')}.{thread.created_at.strftime('%f')[0:3]} ID:{thread.account_id}<> {thread.content} <>{thread.title}"
    )

    for response in responses:
        response.created_at = response.created_at.astimezone(ZoneInfo("Asia/Tokyo"))
        response.content = response.content.replace("\n", " <br> ")

        threadDat.append(
            f"{response.name}<><>{response.created_at.strftime('%Y/%m/%d')}({weekdays[response.created_at.weekday()]}) {response.created_at.strftime('%H:%M:%S')}.{response.created_at.strftime('%f')[0:3]} ID:{response.account_id}<> {response.content} <>"
        )

    threadDat.append("")
    return PlainTextResponse(
        "\n".join(threadDat)
        .encode("ascii", "xmlcharrefreplace")
        .decode()
        .encode("shift_jis"),
        200,
        headers={"content-type": "text/plain; charset=shift_jis"},
    )
