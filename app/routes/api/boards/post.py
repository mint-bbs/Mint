import re
import html
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Cookie, Response
from pydantic import BaseModel

from ....services.board import BoardService
from ....services.thread import ThreadService
from ....services.auth import AuthService
from ....services.trip import TripService

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
    boardName: str,
    model: ThreadPostBody,
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
            raise HTTPException(status_code=401, detail="認証が必要です。")

    authUser = await AuthService.authCheck(chCookie)
    if not authUser:
        raise HTTPException(status_code=401, detail="認証キーが不正です。")

    board = await BoardService.getBoard(boardName)
    if not board:
        raise HTTPException(status_code=404, detail="板が見つかりませんでした。")

    model.name = (
        TripService.tripper(html.escape(model.name))
        if model.name != ""
        else board.anonymous_name
    )
    if len(model.name) > board.name_count:
        raise HTTPException(
            status_code=413,
            detail=f"名前が指定されたサイズより長いです。短くしてください。({len(model.name)} > {board.name_count})",
        )
    model.content = html.escape(model.content)
    if len(model.content) > board.message_count:
        raise HTTPException(
            status_code=413,
            detail=f"本文が指定されたサイズより長いです。短くしてください。({len(model.content)} > {board.message_count})",
        )
    model.title = html.escape(model.title)
    if len(model.title) > board.subject_count:
        raise HTTPException(
            status_code=413,
            detail=f"スレッドのタイトルが指定されたサイズより長いです。短くしてください。({len(model.title)} > {board.subject_count})",
        )

    timestamp = int(datetime.now().timestamp())
    newThread = await BoardService.write(
        board.id,
        timestamp=timestamp,
        title=model.title,
        name=model.name,
        account_id=authUser["account_id"],
        content=model.content,
    )
    response.set_cookie("2ch_X", chCookie)
    return {"detail": "スレッドを建てました！", "thread": newThread}
