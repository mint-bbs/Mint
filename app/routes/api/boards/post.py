import asyncio
import html
import re
from datetime import datetime

import aiodns
from fastapi import APIRouter, BackgroundTasks, Cookie, HTTPException, Request, Response
from pydantic import BaseModel

from ....cloudflare import Cloudflare
from ....events import PostEvent
from ....objects import WriteType
from ....plugin_manager import PluginManager
from ....services.auth import AuthService
from ....services.board import BoardService
from ....services.trip import TripService
from ....sioHandler import sio

router = APIRouter()


class ThreadPostBody(BaseModel):
    title: str
    name: str
    authKey: str
    content: str


@router.put("/api/boards/{boardName:str}")
async def postThread(
    request: Request,
    response: Response,
    backgroundTasks: BackgroundTasks,
    boardName: str,
    model: ThreadPostBody,
    chCookie: str = Cookie(None, alias="2ch_X"),
):
    """
    スレッドを投稿します。
    """

    if (Cloudflare.isCloudflareIP(request.client.host)) and (
        "CF-Connecting-IP" in request.headers
    ):
        ipaddr = request.headers["CF-Connecting-IP"]
    elif "X_FORWARDED_FOR" in request.headers:
        ipaddr = request.headers["X_FORWARDED_FOR"]
    else:
        if not request.client or not request.client.host:
            ipaddr = "127.0.0.1"

        ipaddr = request.client.host

    try:
        resolver = aiodns.DNSResolver(loop=asyncio.get_event_loop())
        result = await resolver.gethostbyaddr(ipaddr)
        ipaddr = result.name
    except aiodns.error.DNSError as e:
        pass

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
            status_code=400,
            detail=f"本文を空欄にすることはできません。",
        )
    model.title = html.escape(model.title).replace("\r", "").replace("\n", "")
    if len(model.title) > board.subject_count:
        raise HTTPException(
            status_code=413,
            detail=f"スレッドのタイトルが指定されたサイズより長いです。短くしてください。({len(model.title)} > {board.subject_count})",
        )

    timestamp = int(datetime.now().timestamp())

    event = PostEvent(
        WriteType.WEBAPI_THREADPOST,
        request=request,
        title=model.title,
        name=model.name,
        accountId=authUser["account_id"],
        mail=model.authKey,
        content=model.content,
        ipaddr=ipaddr,
        board=board,
        timestamp=timestamp,
    )
    for plugin in PluginManager.plugins:
        if getattr(plugin.pluginClass, "onPost", None):
            await plugin.pluginClass.onPost(event)
            if event.isCancelled():
                raise HTTPException(status_code=439, detail=event.getCancelMessage())
            model.title = event.title
            model.name = event.name
            authUser["account_id"] = event.accountId
            model.content = event.content

    newThread = await BoardService.write(
        board.id,
        timestamp=timestamp,
        title=model.title,
        name=model.name,
        account_id=authUser["account_id"],
        content=model.content,
        ipaddr=ipaddr,
    )

    response.set_cookie("2ch_X", chCookie, max_age=60 * 60 * 60 * 24 * 365 * 10)
    if _raw_name != "":
        response.set_cookie("NAME", _raw_name, max_age=60 * 60 * 60 * 24 * 365 * 10)
    else:
        response.set_cookie("NAME", "", max_age=-1)

    backgroundTasks.add_task(
        sio.emit,
        "thread_posted",
        newThread.model_dump_json(),
        room=f"board_{board.id}",
    )

    print(f"board_{board.id}")

    return {"detail": "スレッドを建てました！", "thread": newThread}
