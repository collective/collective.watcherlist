from AccessControl import Unauthorized
from email.utils import formataddr
from email.utils import parseaddr
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.component.hooks import getSite


try:
    from plone.base.utils import safe_text
except ImportError:
    from Products.CMFPlone.utils import safe_text

try:
    # Plone 5
    from plone.registry.interfaces import IRegistry
    from Products.CMFPlone.interfaces.controlpanel import IMailSchema
    from zope.component import getUtility
except ImportError:
    # Plone 4 and lower
    IMailSchema = None
DEFAULT_CHARSET = "utf-8"


def get_charset():
    """Character set to use for encoding the email.

    If encoding fails we will try some other encodings.  We hope
    to get utf-8 here always actually.

    The getSiteEncoding call also works when portal is None, falling
    back to utf-8.  But that is only on Plone 4, not Plone 3.  So we
    handle that ourselves.
    """
    charset = None
    portal = getSite()
    if portal is None:
        return DEFAULT_CHARSET
    if IMailSchema is None:
        # Plone 4
        charset = portal.getProperty("email_charset", "")
    else:
        # Plone 5.0 and higher
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone", check=False)
        charset = mail_settings.email_charset

    if not charset:
        charset = "utf-8"
    return charset


def su(value):
    """Return safe unicode version of value."""
    return safe_text(value, encoding=get_charset())


def get_mail_host():
    """Get the MailHost object.

    Return None in case of problems.
    """
    portal = getSite()
    if portal is None:
        return None
    request = portal.REQUEST
    ctrlOverview = getMultiAdapter((portal, request), name="overview-controlpanel")
    mail_settings_correct = not ctrlOverview.mailhost_warning()
    if mail_settings_correct:
        mail_host = getToolByName(portal, "MailHost", None)
        return mail_host


def get_mail_from_address():
    portal = getSite()
    if portal is None:
        return ""
    if IMailSchema is None:
        # Plone 4
        from_address = portal.getProperty("email_from_address", "")
        from_name = portal.getProperty("email_from_name", "")
    else:
        # Plone 5.0 and higher
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone", check=False)
        from_address = mail_settings.email_from_address
        from_name = mail_settings.email_from_name

    if not from_address:
        return ""
    from_address = from_address.strip()
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
        portal = getSite()
        portal_membership = getToolByName(portal, "portal_membership", None)
        if portal_membership is None:
            # unit test or non-CMF site
            return None

    if username is None:
        member = portal_membership.getAuthenticatedMember()
    else:
        member = portal_membership.getMemberById(username)
    if member is None:
        if username is not None and "@" in username:
            # Use case: explicitly adding a mailing list address
            # to the watchers.
            return username.strip()
        return None

    try:
        email = member.getProperty("email")
    except Unauthorized:
        # this will happen if CMFMember is installed and the email
        # property is protected via AT security
        email = member.getField("email").getAccessor(member)()
    if not email:
        return None
    return email.strip()
