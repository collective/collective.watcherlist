from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope import interface


class IAddToWatchingEvent(IObjectEvent):
    """Event for when a user is added to the watchers list."""


class AddToWatchingEvent(ObjectEvent):
    interface.implements(IAddToWatchingEvent)


class IRemoveFromWatchingEvent(IObjectEvent):
    """Event for when a user is removed from the watchers list."""


class RemoveFromWatchingEvent(ObjectEvent):
    interface.implements(IRemoveFromWatchingEvent)


class IToggleWatchingEvent(IObjectEvent):
    """Event for when a user is added to or removed from the watchers list.
    This event is sent before the add or remove events."""


class ToggleWatchingEvent(ObjectEvent):
    interface.implements(IToggleWatchingEvent)
