"""
fusianasan.py
名前がfusianasanだった場合変換するプラグイン
"""

from app.objects import PluginVersion
from app.events import WriteEvent, PostEvent


class FusianasanPlugin:
    def __init__(self):
        pass

    def fusianasan(self, e: WriteEvent | PostEvent):
        if e.name == "fusianasan":
            e.name = e.request.client.host

    async def onPost(self, e: PostEvent):
        self.fusianasan(e)

    async def onWrite(self, e: WriteEvent):
        self.fusianasan(e)


class MintPluginMetaData:
    name = "fusianasanプラグイン"
    description = "fusianasanを実装します。"
    pluginVersion = "0.0.1"
    mintVersion = PluginVersion.PIERROT
    pluginClass = FusianasanPlugin()
