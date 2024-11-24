from fastapi import Request

from ..objects import Response, Thread
from .base import BaseEvent


class ThreadsRequestEvent(BaseEvent):
    def __init__(self, request: Request, threads: list[Thread]):
        super().__init__()
        self.threads = threads
        self.request = request


class ResponsesRequestEvent(BaseEvent):
    def __init__(self, request: Request, thread: Thread, responses: list[Response]):
        super().__init__()
        self.thread = thread
        self.responses = responses
        self.request = request
