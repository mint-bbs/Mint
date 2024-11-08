import io
import html
from html.parser import HTMLParser

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ...objects import Board
from ...services.board import BoardService
from ...services.meta import MetaDataService

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


@router.get("/{boardName:str}/", response_class=HTMLResponse, include_in_schema=False)
async def boardIndex(request: Request, boardName: str):
    board: Board = await BoardService.getBoard(boardName)
    return templates.TemplateResponse(
        request=request,
        name="board.html",
        context={"board": board, "metadata": MetaDataService.metadata},
    )
