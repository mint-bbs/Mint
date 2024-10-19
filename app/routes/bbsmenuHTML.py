from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..objects import Jinja2SJISTemplates, Board
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

    url = f"{request.url.scheme}://{request.url.hostname}{f':{request.url.port}' if request.url.port is not None else ''}"

    return templates.TemplateResponse(
        request=request,
        name="bbsmenu.html",
        context={
            "request": request,
            "url": url,
            "boards": boards,
            "metadata": MetaDataService.metadata,
        },
        headers={"content-type": "text/html; charset=shift_jis"},
    )
