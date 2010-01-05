import logging
from zope.component import getMultiAdapter
from AccessControl import Unauthorized
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements
import sets

from collective.watcherlist.interfaces import IWatcherList
from collective.watcherlist.mailer import simple_send_mail

logger = logging.getLogger('collective.watcherlist')


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
            self.__mapping = PersistentDict()
            annotations[self.ANNO_KEY] = self.__mapping

    def __get_watchers(self):
        return self.__mapping.get('watchers', PersistentList())

    def __set_watchers(self, v):
        if not isinstance(v, PersistentList):
            v = PersistentList(v)
        self.__mapping['watchers'] = v

    watchers = property(__get_watchers, __set_watchers)

    def __get_extra_addresses(self):
        """Extra email addresses

        # Specific for trackers:
        mailingList = self.getMailingList()
        if mailingList:
            addresses.add(mailingList)
        else:
            addresses.union_update(
              [self._get_member_email(x, portal_membership)
               for x in self.getManagers() or []])

        # Specific for issues:
        addresses.add(issue.getContactEmail())
        """
        return self.__mapping.get('extra_addresses', PersistentList())

    def __set_extra_addresses(self, v):
        if not isinstance(v, PersistentList):
            v = PersistentList(v)
        self.__mapping['extra_addresses'] = v

    extra_addresses = property(__get_extra_addresses, __set_extra_addresses)

    def __get_send_emails(self):
        return self.__mapping.get('send_emails', True)

    def __set_send_emails(self, v):
        if not isinstance(v, bool):
            v = bool(v)
        self.__mapping['send_emails'] = v

    send_emails = property(__get_send_emails, __set_send_emails)

    def getDefaultContactEmail(self):
        """Get the default email address, that of the creating user.

        Taken from PoiIssue, but heavily adapted.

        XXX See extra_addresses
        """
        return self._get_member_email()

    def toggle_watching(self):
        """Add or remove the current authenticated member from the watchers.

        Taken from PoiIssue.
        """
        portal_membership = getToolByName(self.context, 'portal_membership')
        if portal_membership.isAnonymousUser():
            return
        member = portal_membership.getAuthenticatedMember()
        member_id = member.getId()
        if member_id in self.watchers:
            self.watchers.remove(member_id)
        else:
            self.watchers.append(member_id)

    def isWatching(self):
        """
        Determine if the current user is watching this issue or not.

        Taken from PoiIssue.
        """
        portal_membership = getToolByName(self.context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return member.getId() in self.watchers

    def validate_watchers(self, value=None):
        """Make sure watchers are actual user ids.

        Taken from PoiIssue.
        """
        if value is None:
            value = self.watchers
        membership = getToolByName(self.context, 'portal_membership')
        notFound = []
        for userId in value:
            member = membership.getMemberById(userId)
            if member is None:
                notFound.append(userId)
        if notFound:
            return "The following user ids could not be found: %s" % \
                ','.join(notFound)
        else:
            return None

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
            return []

        # make sure no duplicates are added
        addresses = sets.Set()

        context = aq_inner(self.context)
        portal_membership = getToolByName(context, 'portal_membership')
        addresses.union_update([self._get_member_email(w, portal_membership)
                                for w in self.watchers])
        addresses.union_update(self.extra_addresses)

        # Get addresses from parent (might be recursive).
        parent_list = IWatcherList(aq_parent(context), None)
        if parent_list is not None:
            addresses.union_update(parent_list.addresses)

        # Discard invalid addresses:
        addresses.discard(None)
        # Discard current user:
        email = self._get_member_email()
        addresses.discard(email)

        return tuple(addresses)

    def _get_member_email(self, username=None, portal_membership=None):
        """Query portal_membership to figure out the specified email address
        for the given user (via the username parameter) or return None if none
        is present.

        If username is None, we get the currently authenticated user.

        You can pass along portal_membership to avoid having to look
        that up twenty times when you call this method twenty times.

        Taken from PoiTracker.
        """

        if portal_membership is None:
            portal_membership = getToolByName(self.context,
                                              'portal_membership')

        if username is None:
            member = portal_membership.getAuthenticatedMember()
        else:
            member = portal_membership.getMemberById(username)
        if member is None:
            return None

        try:
            email = member.getProperty('email')
        except Unauthorized:
            # this will happen if CMFMember is installed and the email
            # property is protected via AT security
            email = member.getField('email').getAccessor(member)()
        return email

    def send(self, view_name, **kw):
        """Send mail to our addresses using browser view 'view_name'.

        view_name is the name of a browser view for the context.  We
        use that to get the contents and subject of the email.

        Any keyword arguments will be passed along to the update
        method of that view.
        """
        context = aq_inner(self.context)
        addresses = self.addresses
        if not addresses:
            logger.info("No addresses found.")
            return

        request = context.REQUEST
        mail_content = getMultiAdapter((context, request), name=view_name)
        mail_content.update(**kw)
        message = mail_content.prepare_email_message()
        subject = mail_content.subject
        simple_send_mail(message, addresses, subject)
