import html
import io
from html.parser import HTMLParser

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ...objects import Board, Thread
from ...services.board import BoardService
from ...services.meta import MetaDataService
from ...services.thread import ThreadService

router = APIRouter()
templates = Jinja2Templates(directory="pages")


class MyHtmlStripper(HTMLParser):
    def __init__(self, s):
        super().__init__()
        self.sio = io.StringIO()
        self.feed(s)

    def handle_starttag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        self.sio.write(data)

    @property
    def value(self):
        return self.sio.getvalue()


def stripTag(arg: str = None):
    return MyHtmlStripper(html.unescape(str(arg))).value


templates.env.filters["striptag"] = stripTag


@router.get(
    "/test/read.cgi/{boardName:str}/{threadId:int}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def viewThread(request: Request, boardName: str, threadId: int):
    board: Board = await BoardService.getBoard(boardName)
    if not board:
        raise HTTPException(status_code=404)
    thread: Thread = await ThreadService.getThread(board.id, threadId)
    if not thread:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        request=request,
        name="thread.html",
        context={
            "board": board,
            "thread": thread,
            "metadata": MetaDataService.metadata,
        },
    )
