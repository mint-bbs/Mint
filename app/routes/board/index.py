from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ...objects import Board
from ...services.board import BoardService
from ...services.meta import MetaDataService

router = APIRouter()
templates = Jinja2Templates(directory="pages")


@router.get("/{boardName:str}/", response_class=HTMLResponse, include_in_schema=False)
async def boardIndex(request: Request, boardName: str):
    board: Board = await BoardService.getBoard(boardName)
    return templates.TemplateResponse(
        request=request,
        name="board.html",
        context={"board": board, "metadata": MetaDataService.metadata},
    )
