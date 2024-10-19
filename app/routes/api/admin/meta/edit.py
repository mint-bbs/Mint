import asyncpg
import dotenv
from fastapi import APIRouter, Depends

from .....objects import CaptchaType, ChangeableMetaData, MetaData
from .....services.admin import AdminPanelSessionService
from .....services.database import DatabaseService
from .....services.meta import MetaDataService

dotenv.load_dotenv()

router = APIRouter()


@router.patch("/api/admin/meta/edit")
async def editMeta(
    meta: ChangeableMetaData,
    session: dict = Depends(AdminPanelSessionService.sessionCheck),
):
    """メタデータを編集します。"""

    data = meta.model_dump()

    set_clauses = []
    values = [data["id"]]
    idx = 2

    for key, value in data.items():
        if key == "id":
            continue
        print(key, value)
        if value is None:
            set_clauses.append(f"{key} = DEFAULT")
        else:
            set_clauses.append(f"{key} = ${idx}")
            if isinstance(value, CaptchaType):
                values.append(value.value)
            else:
                values.append(value)
            idx += 1

    query = f"""
    UPDATE meta
    SET {', '.join(set_clauses)}
    WHERE id = $1
    RETURNING *
    """

    row = await DatabaseService.pool.fetchrow(query, *values)
    MetaDataService.metadata = MetaData.model_validate(dict(row))
    return {"detail": "success"}
