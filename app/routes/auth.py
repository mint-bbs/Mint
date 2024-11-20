from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..objects import CaptchaType
from ..services.meta import MetaDataService

router = APIRouter()
templates = Jinja2Templates(directory="pages")


@router.get("/auth", response_class=HTMLResponse, include_in_schema=False)
def auth(request: Request):
    if MetaDataService.metadata.captcha_type == CaptchaType.NONE:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        request=request,
        name="auth.html",
        context={"metadata": MetaDataService.metadata, "CaptchaType": CaptchaType},
    )
