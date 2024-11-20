import dotenv
from fastapi import APIRouter, Depends

from .....services.admin import AdminPanelSessionService
from .....services.meta import MetaDataService

dotenv.load_dotenv()

router = APIRouter()


@router.get("/api/admin/meta")
async def data(
    session: dict = Depends(AdminPanelSessionService.sessionCheck),
):
    return MetaDataService.metadata
