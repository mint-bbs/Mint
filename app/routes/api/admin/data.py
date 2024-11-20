import dotenv
from fastapi import APIRouter

from ....services.database import DatabaseService
from ....services.meta import MetaDataService

dotenv.load_dotenv()

router = APIRouter()


@router.get("/api/admin/data")
async def data():
    userCount = await DatabaseService.pool.fetchval(
        "SELECT COUNT(*) FROM admin_panel_users"
    )
    return {"userCount": userCount, "metadata": MetaDataService.metadata.public()}
