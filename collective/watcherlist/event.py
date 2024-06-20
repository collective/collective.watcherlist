from zope import interface
from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent


class IAddedToWatchingEvent(IObjectEvent):
    """Event for when a user is added to the watchers list."""


class AddedToWatchingEvent(ObjectEvent):
    interface.implements(IAddedToWatchingEvent)


class IRemovedFromWatchingEvent(IObjectEvent):
    """Event for when a user is removed from the watchers list."""


class RemovedFromWatchingEvent(ObjectEvent):
    interface.implements(IRemovedFromWatchingEvent)


class IToggleWatchingEvent(IObjectEvent):
    """Event for when a user is added to or removed from the watchers list.
    This event is sent before the add or remove events."""


class ToggleWatchingEvent(ObjectEvent):
    interface.implements(IToggleWatchingEvent)
