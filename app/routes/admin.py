from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..services.meta import MetaDataService

router = APIRouter()
templates = Jinja2Templates(directory="pages")


@router.get("/admin", response_class=HTMLResponse, include_in_schema=False)
def admin(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={"metadata": MetaDataService.metadata},
    )
