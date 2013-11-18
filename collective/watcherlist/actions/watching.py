from OFS.SimpleItem import SimpleItem
from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.contentrules.rule.interfaces import IRuleElementData, IExecutable
from Products.CMFPlone import PloneMessageFactory as _p
from zope.formlib import form
from zope.component import adapts
from zope import component
from zope import interface
from zope import schema

from collective.watcherlist.actions.vocabularies import watchingChoice
from collective.watcherlist.interfaces import IWatcherList
from collective.watcherlist.i18n import _


class IWatchingAction(interface.Interface):
    """Definition of the configuration available for a watching action."""

    watching = schema.Choice(
        title=_(u"Change watching"),
        vocabulary=watchingChoice
        )


class WatchingAction(SimpleItem):
    interface.implements(IWatchingAction, IRuleElementData)

    watching = 'watch'
    element = 'collective.watcherlist.actions.Watching'
    summary = _(u'Change if the user is in the watchers list or not.')


class WatchingActionExecutor(object):
    interface.implements(IExecutable)
    adapts(interface.Interface, IWatchingAction, interface.Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        watching = self.element.watching
        obj = self.event.object
        watchers = component.queryAdapter(
            obj,
            interface=IWatcherList,
            name="group_watchers",
            default=None
            )
        if watching == 'watch' and watchers.isWatching():
            return True
        if watching == 'unwatch' and not watchers.isWatching():
            return True
        watchers.toggle_watching()
        return True


class WatchingActionAddForm(AddForm):
    form_fields = form.FormFields(IWatchingAction)
    label = _(u'Add watching action')
    description = _(u'An action which can add or remove a user '
                    u'from the watchers list')
    form_name = _p(u'Configure element')

    def create(self, data):
        a = WatchingAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class WatchingActionEditForm(EditForm):
    form_fields = form.FormFields(IWatchingAction)
    label = _(u'Edit watching action')
    description = _(u'An action which can add or remove a user '
                    u'from the watchers list')
    form_name = _p(u'Configure element')
