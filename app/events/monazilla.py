from fastapi import Request

from .base import BaseEvent
from ..objects import Thread, Response


class RequestDatEvent(BaseEvent):
    def __init__(self, request: Request, thread: Thread, responses: list[Response]):
        super().__init__()
        self.thread = thread
        self.responses = responses
        self.request = request
