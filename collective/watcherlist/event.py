from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope import interface


class IAddedToWatchingEvent(IObjectEvent):
    """Event for when a user is added to the watchers list."""


@interface.implementer(IAddedToWatchingEvent)
class AddedToWatchingEvent(ObjectEvent):
    """"""


class IRemovedFromWatchingEvent(IObjectEvent):
    """Event for when a user is removed from the watchers list."""


@interface.implementer(IRemovedFromWatchingEvent)
class RemovedFromWatchingEvent(ObjectEvent):
    """"""


class IToggleWatchingEvent(IObjectEvent):
    """Event for when a user is added to or removed from the watchers list.
    This event is sent before the add or remove events."""


@interface.implementer(IToggleWatchingEvent)
class ToggleWatchingEvent(ObjectEvent):
    """"""
