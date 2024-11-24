"""
fusianasan.py
名前がfusianasanだった場合変換するプラグイン
"""

from app.objects import PluginVersion
from app.events import WriteEvent, PostEvent


class FusianasanPlugin:
    def __init__(self):
        self.onWrite = self.write
        self.onPost = self.post

    def fusianasan(self, e: WriteEvent | PostEvent):
        if e.name == "fusianasan":
            e.name = e.request.client.host

    async def post(self, e: PostEvent):
        self.fusianasan(e)

    async def write(self, e: WriteEvent):
        self.fusianasan(e)


class MintPluginMetaData:
    name = "fusianasanプラグイン"
    pluginVersion = "0.0.1"
    mintVersion = PluginVersion.PIERROT
    pluginClass = FusianasanPlugin()
