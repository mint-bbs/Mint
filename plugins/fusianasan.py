"""
fusianasan.py
名前がfusianasanだった場合変換するプラグイン
"""

from app.events import PostEvent, WriteEvent
from app.objects import PluginVersion


class FusianasanPlugin:
    def fusianasan(self, e: WriteEvent | PostEvent):
        if e.name == "fusianasan":
            e.name = e.ipaddr

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
