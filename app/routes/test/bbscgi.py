import html
import re
import urllib
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import HTMLResponse

from ...objects import Jinja2SJISTemplates, Response
from ...services.auth import AuthService
from ...services.board import BoardService
from ...services.thread import ThreadService
from ...services.trip import TripService
from ...sioHandler import sio

router = APIRouter()
templates = Jinja2SJISTemplates(directory="pages")


@router.get("/test/bbs.cgi", response_class=HTMLResponse, include_in_schema=False)
@router.post("/test/bbs.cgi", response_class=HTMLResponse)
async def bbscgi(request: Request, backgroundTasks: BackgroundTasks):
    data = await request.body()
    postDataDict = {}
    for pair in data.decode().split("&"):
        key, value = pair.split("=")
        postDataDict[key] = urllib.parse.unquote(value.replace("+", " "), "cp932")

    bbs = postDataDict.get("bbs", "")
    key = int(postDataDict.get("key", 0))
    time = int(postDataDict.get("time", 0))
    subject = postDataDict.get("subject", "")
    FROM = postDataDict.get("FROM", "")
    mail = postDataDict.get("mail", "")
    MESSAGE = postDataDict.get("MESSAGE", "").replace("\r\n", "\n").replace("\r", "\n")
    submit = postDataDict.get("submit", "")
    chCookie = request.cookies.get("2ch_X", None)

    if "X_FORWARDED_FOR" in request.headers:
        ipaddr = request.headers["X_FORWARDED_FOR"]
    else:
        if not request.client or not request.client.host:
            ipaddr = "127.0.0.1"

        ipaddr = request.client.host

    if not (
        (request.method.lower() != "post")
        or ("書き込む" in submit.encode("utf-8").decode("utf-8"))
        or (not bbs)
        or (not MESSAGE)
        or ((not subject) and (not key))
        or ((subject != None) and (key != None))
    ):
        return templates.TemplateResponse(
            request=request,
            name="bbscgi_error.html",
            context={
                "message": "フォーム情報が正しく読めないです。",
                "ipaddr": ipaddr,
                "bbs": bbs,
                "key": key,
                "FROM": FROM.encode("utf-8").decode("utf-8"),
                "mail": mail.encode("utf-8").decode("utf-8"),
                "MESSAGE": MESSAGE.encode("utf-8").decode("utf-8"),
            },
            headers={"content-type": "text/html; charset=shift_jis"},
        )

    mail = mail.encode("utf-8").decode("utf-8")
    print(mail)
    if not chCookie:
        match = re.match(r"#(.*)", mail)
        print(match)
        if match:
            chCookie = match.group(1)
        else:
            return templates.TemplateResponse(
                request=request,
                name="bbscgi_error.html",
                context={
                    "message": f"あなたは認証していません。 <a href=\"{request.url.scheme}://{request.url.hostname}{f':{request.url.port}' if request.url.port is not None else ''}/auth\">{request.url.scheme}://{request.url.hostname}{f':{request.url.port}' if request.url.port is not None else ''}/auth</a> から認証してください。",
                    "ipaddr": ipaddr,
                    "bbs": bbs,
                    "key": key,
                    "FROM": FROM.encode("utf-8").decode("utf-8"),
                    "mail": mail.encode("utf-8").decode("utf-8"),
                    "MESSAGE": MESSAGE.encode("utf-8").decode("utf-8"),
                },
                headers={"content-type": "text/html; charset=shift_jis"},
            )

    print(chCookie)

    authUser = await AuthService.authCheck(chCookie)
    if not authUser:
        return templates.TemplateResponse(
            request=request,
            name="bbscgi_error.html",
            context={
                "message": f"認証に失敗しました。<a href=\"{request.url.scheme}://{request.url.hostname}{f':{request.url.port}' if request.url.port is not None else ''}/auth\">{request.url.scheme}://{request.url.hostname}{f':{request.url.port}' if request.url.port is not None else ''}/auth</a>から認証してください。",
                "ipaddr": ipaddr,
                "bbs": bbs,
                "key": key,
                "FROM": FROM.encode("utf-8").decode("utf-8"),
                "mail": mail.encode("utf-8").decode("utf-8"),
                "MESSAGE": MESSAGE.encode("utf-8").decode("utf-8"),
            },
            headers={"content-type": "text/html; charset=shift_jis"},
        )

    board = await BoardService.getBoard(bbs)
    if not board:
        return templates.TemplateResponse(
            request=request,
            name="bbscgi_error.html",
            context={
                "message": "板設定が壊れています！",
                "ipaddr": ipaddr,
                "bbs": bbs,
                "key": key,
                "FROM": FROM.encode("utf-8").decode("utf-8"),
                "mail": mail.encode("utf-8").decode("utf-8"),
                "MESSAGE": MESSAGE.encode("utf-8").decode("utf-8"),
            },
            headers={"content-type": "text/html; charset=shift_jis"},
        )

    if key and (key != ""):
        thread = await ThreadService.getThread(bbs, int(key))
        if not thread:
            return templates.TemplateResponse(
                request=request,
                name="bbscgi_error.html",
                context={
                    "message": "スレッドデータが壊れています！",
                    "ipaddr": ipaddr,
                    "bbs": bbs,
                    "key": key,
                    "FROM": FROM.encode("utf-8").decode("utf-8"),
                    "mail": mail.encode("utf-8").decode("utf-8"),
                    "MESSAGE": MESSAGE.encode("utf-8").decode("utf-8"),
                },
                headers={"content-type": "text/html; charset=shift_jis"},
            )

    FROM = (
        TripService.tripper(html.escape(FROM.encode("utf-8").decode("utf-8")))
        if FROM != ""
        else board.anonymous_name
    )
    if len(FROM) > board.name_count:
        return templates.TemplateResponse(
            request=request,
            name="bbscgi_error.html",
            context={
                "message": "名前が長すぎます！",
                "ipaddr": ipaddr,
                "bbs": bbs,
                "key": key,
                "FROM": FROM,
                "mail": mail,
                "MESSAGE": MESSAGE.encode("utf-8").decode("utf-8"),
            },
            headers={"content-type": "text/html; charset=shift_jis"},
        )
    content = html.escape(MESSAGE.encode("utf-8").decode("utf-8"))
    if len(content) > board.message_count:
        return templates.TemplateResponse(
            request=request,
            name="bbscgi_error.html",
            context={
                "message": "本文が長すぎます！",
                "ipaddr": ipaddr,
                "bbs": bbs,
                "key": key,
                "FROM": FROM,
                "mail": mail,
                "MESSAGE": content,
            },
            headers={"content-type": "text/html; charset=shift_jis"},
        )
    if subject:
        subject = html.escape(subject.encode("utf-8").decode("utf-8"))

        if len(subject) > board.subject_count:
            return templates.TemplateResponse(
                request=request,
                name="bbscgi_error.html",
                context={
                    "message": "タイトルが長すぎます！",
                    "ipaddr": ipaddr,
                    "bbs": bbs,
                    "key": key,
                    "FROM": FROM,
                    "mail": mail,
                    "MESSAGE": MESSAGE,
                },
                headers={"content-type": "text/html; charset=shift_jis"},
            )

        timestamp = int(datetime.now().timestamp())
        newThread = await BoardService.write(
            board.id,
            timestamp=timestamp,
            title=subject,
            name=FROM,
            account_id=authUser["account_id"],
            content=content,
        )
        templateResponse = templates.TemplateResponse(
            request=request,
            name="bbscgi_success.html",
            context={
                "bbs": newThread.board,
                "key": newThread.id,
            },
            headers={"content-type": "text/html; charset=shift_jis"},
        )

        templateResponse.set_cookie("2ch_X", chCookie, max_age=365 * 10)

        backgroundTasks.add_task(
            sio.emit,
            "thread_posted",
            newThread.model_dump(),
            room=f"board_{bbs}",
        )

        return templateResponse
    else:
        response: Response = await ThreadService.write(
            board.id,
            int(key),
            name=FROM,
            account_id=authUser["account_id"],
            content=content,
        )
        templateResponse = templates.TemplateResponse(
            request=request,
            name="bbscgi_success.html",
            context={
                "bbs": response.board,
                "key": response.thread_id,
            },
            headers={"content-type": "text/html; charset=shift_jis"},
        )

        templateResponse.set_cookie("2ch_X", chCookie, max_age=365 * 10)

        backgroundTasks.add_task(
            sio.emit,
            "thread_writed",
            response.model_dump(),
            room=f"board_{bbs}_thread_{response.thread_id}",
        )

        return templateResponse
