from zope.interface import implementer
from zope.interface.interfaces import IObjectEvent
from zope.interface.interfaces import ObjectEvent


class IAddedToWatchingEvent(IObjectEvent):
    """Event for when a user is added to the watchers list."""


@implementer(IAddedToWatchingEvent)
class AddedToWatchingEvent(ObjectEvent):
    pass


class IRemovedFromWatchingEvent(IObjectEvent):
    """Event for when a user is removed from the watchers list."""


@implementer(IRemovedFromWatchingEvent)
class RemovedFromWatchingEvent(ObjectEvent):
    pass


class IToggleWatchingEvent(IObjectEvent):
    """Event for when a user is added to or removed from the watchers list.
    This event is sent before the add or remove events."""


@implementer(IToggleWatchingEvent)
class ToggleWatchingEvent(ObjectEvent):
    pass
