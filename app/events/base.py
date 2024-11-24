class BaseEvent:
    def __init__(self):
        self.__isCancelled = False
        self.__cancelMessage = ""

    def setCancelled(self, flag: bool, *, message: str = ""):
        self.__isCancelled = flag
        self.__cancelMessage = message

    def isCancelled(self):
        return self.__isCancelled

    def getCancelMessage(self):
        return self.__cancelMessage
