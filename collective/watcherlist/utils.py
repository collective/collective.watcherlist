try:
    from email.utils import parseaddr, formataddr
except ImportError:
    # BBB for python2.4 (Plone 3)
    from email.Utils import parseaddr, formataddr

from AccessControl import Unauthorized
from plone import api
from plone.api.exc import CannotGetPortalError
from Products.CMFPlone.utils import getSiteEncoding
from Products.CMFPlone.utils import safe_unicode
from zope.component import getMultiAdapter

DEFAULT_CHARSET = 'utf-8'


def get_charset():
    """Character set to use for encoding the email.

    If encoding fails we will try some other encodings.  We hope
    to get utf-8 here always actually.

    The getSiteEncoding call also works when portal is None, falling
    back to utf-8.  But that is only on Plone 4, not Plone 3.  So we
    handle that ourselves.
    """
    charset = None
    try:
        portal = api.portal.get()
    except CannotGetPortalError:
        # unit test or non-CMF site
        return DEFAULT_CHARSET
    charset = portal.getProperty('email_charset', '')
    if not charset:
        charset = getSiteEncoding(portal)
    return charset


def su(value):
    """Return safe unicode version of value.
    """
    return safe_unicode(value, encoding=get_charset())


def get_mail_host():
    """Get the MailHost object.

    Return None in case of problems.
    """
    try:
        portal = api.portal.get()
    except CannotGetPortalError:
        # unit test or non-CMF site
        return None
    request = portal.REQUEST
    ctrlOverview = getMultiAdapter((portal, request),
                                   name='overview-controlpanel')
    mail_settings_correct = not ctrlOverview.mailhost_warning()
    if mail_settings_correct:
        mail_host = api.portal.get_tool('MailHost')
        return mail_host


def get_mail_from_address():
    try:
        portal = api.portal.get()
    except CannotGetPortalError:
        # unit test or non-CMF site
        return ''
    from_address = portal.getProperty('email_from_address', '')
    from_name = portal.getProperty('email_from_name', '')
    mfrom = formataddr((from_name, from_address))
    if parseaddr(mfrom)[1] != from_address:
        # formataddr probably got confused by special characters.
        mfrom = from_address
    return mfrom


def get_member_email(username=None, portal_membership=None):
    """Query portal_membership to figure out the specified email address
    for the given user (via the username parameter) or return None if none
    is present.

    If username is None, we get the currently authenticated user.

    You can pass along portal_membership to avoid having to look
    that up twenty times when you call this method twenty times.

    Taken from PoiTracker.
    """
    if portal_membership is None:
        try:
            portal_membership = api.portal.get_tool('portal_membership')
        except CannotGetPortalError:
            # unit test or non-CMF site
            return None

    if username is None:
        member = portal_membership.getAuthenticatedMember()
    else:
        member = portal_membership.getMemberById(username)
    if member is None:
        if username is not None and '@' in username:
            # Use case: explicitly adding a mailing list address
            # to the watchers.
            return username
        return None

    try:
        email = member.getProperty('email')
    except Unauthorized:
        # this will happen if CMFMember is installed and the email
        # property is protected via AT security
        email = member.getField('email').getAccessor(member)()
    return email
