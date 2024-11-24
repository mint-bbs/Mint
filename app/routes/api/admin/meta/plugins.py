import dotenv
from fastapi import APIRouter, Depends

from .....plugin_manager import PluginManager
from .....services.admin import AdminPanelSessionService

dotenv.load_dotenv()

router = APIRouter()


@router.get("/api/admin/meta/plugins")
async def plugins(
    session: dict = Depends(AdminPanelSessionService.sessionCheck),
):
    plugins = []
    for plugin in PluginManager.plugins:
        plugins.append(
            {
                "name": plugin.name,
                "description": plugin.description,
                "pluginVersion": plugin.pluginVersion,
                "mintVersion": plugin.mintVersion,
            }
        )
    return plugins
