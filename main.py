import asyncio
import importlib
import logging
import os
import traceback
from pathlib import Path
from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles

from app.objects import PluginVersion
from app.services.database import DatabaseService
from app.services.meta import MetaDataService
from app.sioHandler import sio
from app.plugin_manager import PluginManager

# This is Mint version! Don't change this!
__mintName__ = "Mint"
__mintFrontName__ = "MintBBS"
__mintVersion__ = "0.1.1"
__mintCodeName__ = "Pierrot"
__mintPluginVersion__ = PluginVersion.PIERROT


def loadPlugins():
    directory = Path("./plugins/")
    files = list(directory.glob("*.py"))

    for file in files:
        module_name = file.stem

        if module_name == "__init__":
            continue

        try:
            module = importlib.import_module(f"plugins.{module_name}")
            meta = getattr(module, "MintPluginMetaData")
            if not meta:
                logging.getLogger("uvicorn").info(
                    f'Plugin file "{module_name}.py" isn\'t Mint Plugin!'
                )
            if meta.mintVersion != __mintPluginVersion__:
                logging.getLogger("uvicorn").info(
                    f"Plugin {meta.name} (v{meta.pluginVersion}) is not compatible with current Mint version"
                )
            PluginManager.plugins.append(module.MintPluginMetaData)
            logging.getLogger("uvicorn").info(
                f"Plugin {meta.name} (v{meta.pluginVersion}) was loaded!"
            )
        except:
            traceback.print_exc()
            continue


@asynccontextmanager
async def lifespan(app: FastAPI):
    await DatabaseService.connect()
    logging.getLogger("uvicorn").info("Loading metadata...")
    await MetaDataService.load(name=__mintFrontName__)
    logging.getLogger("uvicorn").info(
        f"Metadata {MetaDataService.metadata.name} (ID: {MetaDataService.metadata.id}) was loaded!"
    )

    # Plugin Loader
    logging.getLogger("uvicorn").info("Loading plugins...")
    loadPlugins()
    logging.getLogger("uvicorn").info(
        f"{len(PluginManager.plugins)} plugins was loaded!"
    )

    logging.getLogger("uvicorn").info("Ready!")

    yield
    async with asyncio.timeout(60):
        await DatabaseService.pool.close()


fastapi = FastAPI(
    title=__mintName__,
    version=__mintVersion__,
    summary=f"{__mintName__} v{__mintVersion__} Codename: {__mintCodeName__}",
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
)

app = socketio.ASGIApp(sio, fastapi)

fastapi.mount("/static", StaticFiles(directory="static"), name="static")

routes_dir = "app/routes"


def autoIncludeRouters(app: FastAPI, base_dir: str):
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_path = (
                    os.path.join(root, file).replace("/", ".").replace("\\", ".")[:-3]
                )

                module = importlib.import_module(module_path)

                if hasattr(module, "router"):
                    app.include_router(getattr(module, "router"))


autoIncludeRouters(fastapi, routes_dir)
