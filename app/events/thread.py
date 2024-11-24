from fastapi import Request

from .base import BaseEvent
from ..objects import WriteType, Board, Thread


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
        board: Board,
    ):
        super().__init__()

        self.type = type
        self.title = title
        self.name = name
        self.accountId = accountId
        self.mail = mail
        self.content = content
        self.request = request
        self.board = board
