from .base import NotCancellableBaseEvent


class ReadyEvent(NotCancellableBaseEvent):
    def __init__(self):
        super().__init__()
