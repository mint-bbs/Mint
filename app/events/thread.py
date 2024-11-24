from fastapi import Request

from ..objects import Board, Thread, WriteType
from .base import BaseEvent


class WriteEvent(BaseEvent):
    def __init__(
        self,
        type: WriteType,
        *,
        request: Request,
        name: str,
        accountId: str,
        mail: str,
        content: str,
        ipaddr: str,
        board: Board,
        thread: Thread,
    ):
        super().__init__()

        self.type = type
        self.name = name
        self.accountId = accountId
        self.mail = mail
        self.content = content
        self.request = request
        self.ipaddr = ipaddr
        self.board = board
        self.thread = thread


class PostEvent(BaseEvent):
    def __init__(
        self,
        type: WriteType,
        *,
        request: Request,
        title: str,
        name: str,
        accountId: str,
        mail: str,
        content: str,
        ipaddr: str,
        board: Board,
    ):
        super().__init__()

        self.type = type
        self.title = title
        self.name = name
        self.accountId = accountId
        self.mail = mail
        self.content = content
        self.ipaddr = ipaddr
        self.request = request
        self.board = board
