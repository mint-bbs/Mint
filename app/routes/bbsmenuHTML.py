from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..objects import Board, Jinja2SJISTemplates
from ..services.database import DatabaseService
from ..services.meta import MetaDataService

router = APIRouter()
templates = Jinja2SJISTemplates(directory="pages")


@router.get("/bbsmenu.html", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    rows = await DatabaseService.pool.fetch("SELECT * FROM boards")
    if not rows:
        return []
    boards = []
    for row in rows:
        boards.append(Board.model_validate(dict(row)))

    return templates.TemplateResponse(
        request=request,
        name="bbsmenu.html",
        context={
            "request": request,
            "boards": boards,
            "metadata": MetaDataService.metadata,
        },
        headers={"content-type": "text/html; charset=shift_jis"},
    )
