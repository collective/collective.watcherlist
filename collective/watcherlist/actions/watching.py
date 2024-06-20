from collective.watcherlist.actions.vocabularies import watchingChoice
from collective.watcherlist.i18n import _
from collective.watcherlist.interfaces import IWatcherList
from OFS.SimpleItem import SimpleItem
from plone.app.contentrules.browser.formhelper import AddForm
from plone.app.contentrules.browser.formhelper import EditForm
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from Products.CMFPlone import PloneMessageFactory as _p
from zope import component
from zope import interface
from zope import schema
from zope.component import adapts
from zope.formlib import form


class IWatchingAction(interface.Interface):
    """Definition of the configuration available for a watching action."""

    watching = schema.Choice(title=_("Change watching"), vocabulary=watchingChoice)

    name = schema.ASCIILine(
        title=_("Name of your adapter"),
        description=_("Leave that empty if you don't" " know what you're doing."),
        missing_value="",
        required=False,
    )


class WatchingAction(SimpleItem):
    interface.implements(IWatchingAction, IRuleElementData)

    watching = "watch"
    name = ""
    element = "collective.watcherlist.actions.Watching"
    summary = _("Change if the user is in the watchers list or not.")


class WatchingActionExecutor:
    interface.implements(IExecutable)
    adapts(interface.Interface, IWatchingAction, interface.Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        watching = self.element.watching
        name = self.element.name
        obj = self.event.object
        watchers = component.queryAdapter(
            obj, interface=IWatcherList, name=name, default=None
        )
        if watchers is None:
            return False
        if watching == "watch" and watchers.isWatching():
            return True
        if watching == "unwatch" and not watchers.isWatching():
            return True
        watchers.toggle_watching()
        return True


class WatchingActionAddForm(AddForm):
    form_fields = form.FormFields(IWatchingAction)
    label = _("Add watching action")
    description = _(
        "An action which can add or remove a user " "from the watchers list"
    )
    form_name = _p("Configure element")

    def create(self, data):
        a = WatchingAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class WatchingActionEditForm(EditForm):
    form_fields = form.FormFields(IWatchingAction)
    label = _("Edit watching action")
    description = _(
        "An action which can add or remove a user " "from the watchers list"
    )
    form_name = _p("Configure element")
