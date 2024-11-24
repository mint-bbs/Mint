"""
テンプレートプラグイン
"""

from app.events import (
    DatRequestEvent,
    PostEvent,
    ReadyEvent,
    ResponsesRequestEvent,
    ThreadsRequestEvent,
    WriteEvent,
)
from app.objects import PluginVersion


class TemplatePlugin:
    async def onReady(self, e: ReadyEvent):
        # プラグインがロードされ、準備が完了したとき
        pass

    async def onPost(self, e: PostEvent):
        # スレッドが投稿されたとき
        pass

    async def onWrite(self, e: WriteEvent):
        # スレッドにレスがついたとき
        pass

    async def onDatRequest(self, e: DatRequestEvent):
        # .datがリクエストされたとき
        pass

    async def onThreadsRequest(self, e: ThreadsRequestEvent):
        # スレッドの一覧がAPIによってリクエストされたとき
        pass

    async def onResponsesRequest(self, e: ResponsesRequestEvent):
        # レスがAPIによってリクエストされたとき
        pass


class MintPluginMetaData:
    name = "テンプレートプラグイン"
    description = "プラグインのテンプレートです。"
    pluginVersion = "0.0.1"
    mintVersion = PluginVersion.PIERROT
    pluginClass = TemplatePlugin()
