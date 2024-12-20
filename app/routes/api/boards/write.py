import html
import re

import orjson
from fastapi import APIRouter, BackgroundTasks, Cookie, HTTPException, Request, Response
from pydantic import BaseModel

from .... import objects
from ....services.auth import AuthService
from ....services.board import BoardService
from ....services.thread import ThreadService
from ....services.trip import TripService
from ....sioHandler import sio

router = APIRouter()


class ResponseWriteBody(BaseModel):
    name: str
    authKey: str
    content: str


@router.put("/api/boards/{boardName:str}/threads/{threadId:int}")
async def postThread(
    request: Request,
    response: Response,
    backgroundTasks: BackgroundTasks,
    boardName: str,
    threadId: int,
    model: ResponseWriteBody,
    chCookie: str = Cookie(None, alias="2ch_X"),
):
    """
    スレッドを投稿します。
    """

    if "X_FORWARDED_FOR" in request.headers:
        ipaddr = request.headers["X_FORWARDED_FOR"]
    else:
        if not request.client or not request.client.host:
            ipaddr = "127.0.0.1"

        ipaddr = request.client.host

    if not chCookie:
        match = re.match(r"#(.*)", model.authKey)
        if match:
            chCookie = match.group(1)
        else:
            raise HTTPException(
                status_code=401,
                detail="認証が必要です。<a href='/auth'>ここから認証</a>してください。",
            )

    authUser = await AuthService.authCheck(chCookie)
    if not authUser:
        raise HTTPException(status_code=401, detail="認証キーが不正です。")

    board = await BoardService.getBoard(boardName)
    if not board:
        raise HTTPException(status_code=404, detail="板が見つかりませんでした。")

    thread = await ThreadService.getThread(board.id, threadId)
    if not thread:
        raise HTTPException(status_code=404, detail="スレッドが見つかりませんでした。")

    _raw_name = model.name

    model.name = (
        (
            TripService.tripper(html.escape(model.name))
            if model.name != ""
            else board.anonymous_name
        )
        .replace("\r", "")
        .replace("\n", "")
    )
    if len(model.name) > board.name_count:
        raise HTTPException(
            status_code=413,
            detail=f"名前が指定されたサイズより長いです。短くしてください。({len(model.name)} > {board.name_count})",
        )

    model.content = (
        html.escape(model.content.strip()).replace("\r\n", "\n").replace("\r", "\n")
    )
    if model.content == "":
        raise HTTPException(
            status_code=401,
            detail=f"本文を空欄にすることはできません。",
        )
    if len(model.content) > board.message_count:
        raise HTTPException(
            status_code=413,
            detail=f"本文が指定されたサイズより長いです。短くしてください。({len(model.content)} > {board.message_count})",
        )

    newResponse: objects.Response = await ThreadService.write(
        board.id,
        thread.id,
        name=model.name,
        account_id=authUser["account_id"],
        content=model.content,
        count=thread.count + 1,
        ipaddr=ipaddr,
    )

    response.set_cookie("2ch_X", chCookie, max_age=60 * 60 * 60 * 24 * 365 * 10)
    response.set_cookie("NAME", _raw_name, max_age=60 * 60 * 60 * 24 * 365 * 10)

    backgroundTasks.add_task(
        sio.emit,
        "thread_writed",
        newResponse.model_dump_json(),
        room=f"thread_{newResponse.thread_id}",
    )

    async def threadPositionChanged(board: objects.Board):
        json = await ThreadService.getThreads(board.id, limit=50, json=True)
        await sio.emit("thread_position_changed", json, room=f"board_{board.id}")

    backgroundTasks.add_task(threadPositionChanged, board)

    return {"detail": "スレッドに書き込みました！", "response": newResponse}
