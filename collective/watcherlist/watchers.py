import logging
from zope.component import getMultiAdapter
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
from zope.interface import implements
import sets

from collective.watcherlist.interfaces import IWatcherList
from collective.watcherlist.mailer import simple_send_mail
from collective.watcherlist.utils import get_member_email
from collective.watcherlist import event

logger = logging.getLogger('collective.watcherlist')

_marker = object()


class WatcherList(object):
    """Adapter for lists of watchers.

    The lists are stored on the content objects that are being
    watched.

    XXX Watchers: perhaps for each watcher keep some configuration
    like this:

    - wants plain/html

    - list of mails they are interested in; for xm that could be:
      task-started (for assignees) and task-completed (for creator);
      an empty list means: give me everything.

    """

    implements(IWatcherList)
    ANNO_KEY = 'collective.watcherlist'

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(self.context)
        self.__mapping = annotations.get(self.ANNO_KEY, None)
        if self.__mapping is None:
            info = dict(
                watchers=PersistentList(),
                extra_addresses=PersistentList())
            self.__mapping = PersistentDict(info)
            annotations[self.ANNO_KEY] = self.__mapping

    def __get_watchers(self):
        return self.__mapping.get('watchers')

    def __set_watchers(self, v):
        if not isinstance(v, PersistentList):
            v = PersistentList(v)
        self.__mapping['watchers'] = v

    watchers = property(__get_watchers, __set_watchers)

    def __get_extra_addresses(self):
        """Extra email addresses
        """
        return self.__mapping.get('extra_addresses')

    def __set_extra_addresses(self, v):
        if not isinstance(v, PersistentList):
            v = PersistentList(v)
        self.__mapping['extra_addresses'] = v

    extra_addresses = property(__get_extra_addresses, __set_extra_addresses)

    def __get_send_emails(self):
        """Should emails be sent?

        The parent of the context may have a setting for this.  In the
        context we may or may not wish to override this.  For example,
        in the case of Poi we only set this on the tracker, not on
        individual issues.
        """
        setting = self.__mapping.get('send_emails', _marker)
        if setting is not _marker:
            # We have an explicit setting.
            return setting
        # The context has no explicit setting, so we ask the parent.
        context = aq_inner(self.context)
        parent_list = IWatcherList(aq_parent(context), None)
        if parent_list is not None:
            return parent_list.send_emails

        # No explicit setting, so we fall back to the default: yes, we
        # send emails.
        return True

    def __set_send_emails(self, v):
        if not isinstance(v, bool):
            v = bool(v)
        self.__mapping['send_emails'] = v

    send_emails = property(__get_send_emails, __set_send_emails)

    def append(self, item):
        notify(event.ToggleWatchingEvent(self.context))
        notify(event.AddedToWatchingEvent(self.context))
        self.watchers.append(item)

    def remove(self, item):
        notify(event.ToggleWatchingEvent(self.context))
        notify(event.RemovedFromWatchingEvent(self.context))
        self.watchers.remove(item)

    def toggle_watching(self):
        """Add or remove the current authenticated member from the watchers.

        Taken from PoiIssue.

        If the current value is a tuple, we keep it that way.
        """
        memship = getToolByName(self.context, 'portal_membership', None)
        if memship is None:
            return
        if memship.isAnonymousUser():
            return
        member = memship.getAuthenticatedMember()
        member_id = member.getId()
        watchers = self.watchers
        if isinstance(watchers, tuple):
            watchers = list(watchers)
            as_tuple = True
        else:
            as_tuple = False
        if member_id in self.watchers:
            notify(event.ToggleWatchingEvent(self.context))
            notify(event.RemovedFromWatchingEvent(self.context))
            watchers.remove(member_id)
        else:
            notify(event.ToggleWatchingEvent(self.context))
            notify(event.AddedToWatchingEvent(self.context))
            watchers.append(member_id)
        if as_tuple:
            self.watchers = tuple(watchers)

    def isWatching(self):
        """
        Determine if the current user is watching this issue or not.

        Taken from PoiIssue.
        """
        memship = getToolByName(self.context, 'portal_membership', None)
        if memship is None:
            return False
        member = memship.getAuthenticatedMember()
        if member is None:
            return False
        return member.getId() in self.watchers

    @property
    def addresses(self):
        """
        Upon activity for the given issue, get the list of email
        addresses to which notifications should be sent. May return an
        empty list if notification is turned off. If issue is given, the
        issue poster and any watchers will also be included.

        Taken from PoiTracker.

        Note that we currently return only email addresses, without
        any full names.  That is what Poi has been doing, and it makes
        a few things simpler.
        """
        if not self.send_emails:
            return ()

        # make sure no duplicates are added
        addresses = sets.Set()

        context = aq_inner(self.context)
        memship = getToolByName(context, 'portal_membership', None)
        if memship is None:
            # Okay, either we are in a simple unit test, or someone is
            # using this package outside of CMF/Plone.  We should
            # assume the watchers are simple email addresses.
            addresses.union_update(self.watchers)
        else:
            addresses.union_update([get_member_email(w, memship)
                                    for w in self.watchers])
        addresses.union_update(self.extra_addresses)

        # Get addresses from parent (might be recursive).
        parent_list = IWatcherList(aq_parent(context), None)
        if parent_list is not None:
            addresses.union_update(parent_list.addresses)

        # Discard invalid addresses:
        addresses.discard(None)
        # Discard current user:
        email = get_member_email()
        addresses.discard(email)

        return tuple(addresses)

    def send(self, view_name, only_these_addresses=None, **kw):
        """Send mail to our addresses using browser view 'view_name'.

        view_name is the name of a browser view for the context.  We
        use that to get the contents and subject of the email.

        only_these_addresses is a list of addresses; this forces
        sending only to those addresses and ignoring all others.

        Any keyword arguments will be passed along to the update
        method of that view.
        """
        context = aq_inner(self.context)
        if only_these_addresses is None:
            addresses = self.addresses
        else:
            addresses = only_these_addresses
        if not addresses:
            logger.info("No addresses found.")
            return
        if isinstance(addresses, basestring):
            addresses = [addresses]

        request = context.REQUEST
        mail_content = getMultiAdapter((context, request), name=view_name)
        mail_content.update(**kw)
        message = mail_content.prepare_email_message()
        if not message:
            logger.warn("Not sending empty email.")
            return
        subject = mail_content.subject
        simple_send_mail(message, addresses, subject)
