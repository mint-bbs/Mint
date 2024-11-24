from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from ...services.board import BoardService

router = APIRouter()


@router.get(
    "/{boardName:str}/SETTING.TXT",
    response_class=PlainTextResponse,
)
async def settingTXT(boardName: str):
    """
    Monazilla 1.0の形式の板設定。
    """
    board = await BoardService.getBoard(boardName)
    if not board:
        raise HTTPException(status_code=404)
    setting = f"""BBS_TITLE={board.name}
BBS_TITLE_PICTURE=/static/img/mint.png
BBS_TITLE_COLOR=#000000
BBS_TITLE_LINK=
BBS_BG_COLOR=#FFFFFF
BBS_BG_PICTURE=/static/img/ba.gif
BBS_NONAME_NAME={board.anonymous_name}
BBS_MAKETHREAD_COLOR=#CCFFCC
BBS_MENU_COLOR=#CCFFCC
BBS_THREAD_COLOR=#EFEFEF
BBS_TEXT_COLOR=#000000
BBS_NAME_COLOR=green
BBS_LINK_COLOR=#0000FF
BBS_ALINK_COLOR=#FF0000
BBS_VLINK_COLOR=#AA0088
BBS_THREAD_NUMBER=10
BBS_CONTENTS_NUMBER=10
BBS_LINE_NUMBER=40
BBS_MAX_MENU_THREAD=30
BBS_SUBJECT_COLOR=#FF0000
BBS_PASSWORD_CHECK=
BBS_UNICODE=change
BBS_DELETE_NAME={board.deleted_name}
BBS_NAMECOOKIE_CHECK=checked
BBS_MAILCOOKIE_CHECK=checked
BBS_SUBJECT_COUNT={board.subject_count}
BBS_NAME_COUNT={board.name_count}
BBS_MAIL_COUNT=2048
BBS_MESSAGE_COUNT={board.message_count}
BBS_NEWSUBJECT=1
BBS_THREAD_TATESUGI=5
BBS_AD2=
SUBBBS_CGI_ON=1
NANASHI_CHECK=
timecount=7
timeclose=5
BBS_PROXY_CHECK=
BBS_OVERSEA_THREAD=
BBS_OVERSEA_PROXY=
BBS_RAWIP_CHECK=
BBS_SLIP=
BBS_DISP_IP=
BBS_FORCE_ID=checked
BBS_BE_ID=
BBS_BE_TYPE2=
BBS_NO_ID=
BBS_JP_CHECK=
BBS_VIP931=
BBS_4WORLD=
BBS_YMD_WEEKS=日/月/火/水/木/金/土
BBS_NINJA=
BBS_CAP_COLOR=
BBS_COLUMN_NUMBER=256
BBS_COOKIEPATH=/
BBS_DATMAX=512
BBS_HOUSHITIME=
BBS_INDEX_LINE_NUMBER=12
BBS_READONLY=none
BBS_REFERER_CUSHION=
BBS_RES_MAX=
BBS_SAMBATIME=
BBS_SUBJECT_MAX=
BBS_SUBTITLE={board.name}
BBS_TATESUGI_COUNT=5
BBS_TATESUGI_COUNT2=1
BBS_TATESUGI_HOUR=0
BBS_THREADCAPONLY=
BBS_THREADMOBILE=
"""
    return PlainTextResponse(
        setting.encode("ascii", "xmlcharrefreplace").decode().encode("shift_jis"),
        200,
        headers={"content-type": "text/plain; charset=shift_jis"},
    )
