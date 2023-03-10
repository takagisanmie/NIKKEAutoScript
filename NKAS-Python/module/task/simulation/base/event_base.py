
from module.base.base import BaseModule


class BaseEvent(BaseModule):
    def __init__(self, eventType, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.eventType = eventType
        self.parent = parent
