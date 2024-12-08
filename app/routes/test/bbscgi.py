import asyncio
import html
import re
import urllib
from datetime import datetime

import aiodns
from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import HTMLResponse

from ...cloudflare import Cloudflare
from ...events import PostEvent, WriteEvent
from ...objects import Board, Jinja2SJISTemplates, Response, WriteType
from ...plugin_manager import PluginManager
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

        if thread.count >= 1000:
            return templates.TemplateResponse(
                request=request,
                name="bbscgi_error.html",
                context={
                    "message": "もうお腹いっぱい。。。",
                    "ipaddr": ipaddr,
                    "bbs": bbs,
                    "key": key,
                    "FROM": FROM.encode("utf-8").decode("utf-8"),
                    "mail": mail.encode("utf-8").decode("utf-8"),
                    "MESSAGE": MESSAGE.encode("utf-8").decode("utf-8"),
                },
                headers={"content-type": "text/html; charset=shift_jis"},
            )

    _raw_name = FROM.encode("utf-8").decode("utf-8")

    FROM = (
        (
            TripService.tripper(html.escape(_raw_name))
            if FROM != ""
            else board.anonymous_name
        )
        .replace("\r", "")
        .replace("\n", "")
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
    content = (
        html.escape(MESSAGE.encode("utf-8").decode("utf-8").strip())
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )
    if content == "":
        return templates.TemplateResponse(
            request=request,
            name="bbscgi_error.html",
            context={
                "message": "本文を空欄にすることはできません！",
                "ipaddr": ipaddr,
                "bbs": bbs,
                "key": key,
                "FROM": FROM,
                "mail": mail,
                "MESSAGE": content,
            },
            headers={"content-type": "text/html; charset=shift_jis"},
        )
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
        subject = (
            html.escape(subject.encode("utf-8").decode("utf-8"))
            .replace("\r", "")
            .replace("\n", "")
        )

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

        event = PostEvent(
            WriteType.MONAZILLA_THREADPOST,
            request=request,
            title=subject,
            name=FROM,
            accountId=authUser["account_id"],
            mail=mail,
            content=MESSAGE,
            ipaddr=ipaddr,
            board=board,
            timestamp=timestamp,
        )
        for plugin in PluginManager.plugins:
            if getattr(plugin.pluginClass, "onPost", None):
                await plugin.pluginClass.onPost(event)
                if event.isCancelled():
                    return templates.TemplateResponse(
                        request=request,
                        name="bbscgi_error.html",
                        context={
                            "message": event.getCancelMessage(),
                            "ipaddr": ipaddr,
                            "bbs": bbs,
                            "key": key,
                            "FROM": FROM,
                            "mail": mail,
                            "MESSAGE": MESSAGE,
                        },
                        headers={"content-type": "text/html; charset=shift_jis"},
                    )
                subject = event.title
                FROM = event.name
                authUser["account_id"] = event.accountId
                MESSAGE = event.content

        newThread = await BoardService.write(
            board.id,
            timestamp=timestamp,
            title=subject,
            name=FROM,
            account_id=authUser["account_id"],
            content=content,
            ipaddr=ipaddr,
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

        templateResponse.set_cookie(
            "2ch_X", chCookie, max_age=60 * 60 * 60 * 24 * 365 * 10
        )
        templateResponse.set_cookie(
            "NAME", _raw_name, max_age=60 * 60 * 60 * 24 * 365 * 10
        )

        backgroundTasks.add_task(
            sio.emit,
            "thread_posted",
            newThread.model_dump_json(),
            room=f"board_{bbs}",
        )

        return templateResponse
    else:
        event = WriteEvent(
            WriteType.MONAZILLA_THREADWRITE,
            request=request,
            name=FROM,
            accountId=authUser["account_id"],
            mail=mail,
            content=MESSAGE,
            ipaddr=ipaddr,
            board=board,
            thread=thread,
        )
        for plugin in PluginManager.plugins:
            if getattr(plugin.pluginClass, "onWrite", None):
                await plugin.pluginClass.onWrite(event)
                if event.isCancelled():
                    return templates.TemplateResponse(
                        request=request,
                        name="bbscgi_error.html",
                        context={
                            "message": event.getCancelMessage(),
                            "ipaddr": ipaddr,
                            "bbs": bbs,
                            "key": key,
                            "FROM": FROM,
                            "mail": mail,
                            "MESSAGE": MESSAGE,
                        },
                        headers={"content-type": "text/html; charset=shift_jis"},
                    )
                FROM = event.name
                authUser["account_id"] = event.accountId
                MESSAGE = event.content

        response: Response = await ThreadService.write(
            board.id,
            thread.id,
            name=FROM,
            account_id=authUser["account_id"],
            content=content,
            count=thread.count + 1,
            ipaddr=ipaddr,
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

        templateResponse.set_cookie(
            "2ch_X", chCookie, max_age=60 * 60 * 60 * 24 * 365 * 10
        )
        if _raw_name != "":
            templateResponse.set_cookie(
                "NAME", _raw_name, max_age=60 * 60 * 60 * 24 * 365 * 10
            )
        else:
            templateResponse.set_cookie("NAME", "", max_age=-1)

        backgroundTasks.add_task(
            sio.emit,
            "thread_writed",
            response.model_dump_json(),
            room=f"board_{board.id}_thread_{response.thread_id}",
        )

        async def threadPositionChanged(board: Board):
            json = await ThreadService.getThreads(board.id, limit=50, json=True)
            await sio.emit("thread_position_changed", json, room=f"board_{board.id}")

        backgroundTasks.add_task(threadPositionChanged, board)

        return templateResponse
