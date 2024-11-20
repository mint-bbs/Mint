from fastapi import APIRouter, HTTPException

from ....services.board import BoardService

router = APIRouter()


@router.get("/api/boards/{boardName:str}")
async def boardInfo(boardName: str):
    """
    板の情報をJSONで返します。
    """

    board = await BoardService.getBoard(boardName)
    if not board:
        raise HTTPException(status_code=404)
    return board
