try:
    from email.utils import parseaddr
    from email.utils import formataddr
except ImportError:
    # BBB for python2.4 if we want that.
    from email.Utils import parseaddr
    from email.Utils import formataddr

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getSiteEncoding
from Products.CMFPlone.utils import safe_unicode
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter


def get_charset():
    """Character set to use for encoding the email.

    If encoding fails we will try some other encodings.  We hope
    to get utf-8 here always actually.
    """
    portal = getSite()
    charset = portal.getProperty('email_charset', '')
    if not charset:
        charset = getSiteEncoding()
    return charset


def su(value):
    """Return safe unicode version of value.
    """
    return safe_unicode(value, encoding=get_charset())


def get_mail_host():
    """Get the MailHost object.

    Return None in case of problems.
    """
    portal = getSite()
    request = portal.REQUEST
    ctrlOverview = getMultiAdapter((portal, request),
                                   name='overview-controlpanel')
    mail_settings_correct = not ctrlOverview.mailhost_warning()
    if not mail_settings_correct:
        return None
    mail_host = getToolByName(portal, 'MailHost')
    return mail_host


def get_mail_from_address():
    portal = getSite()
    from_address = portal.getProperty('email_from_address', '')
    from_name = portal.getProperty('email_from_name', '')
    mfrom = formataddr((from_name, from_address))
    if parseaddr(mfrom)[1] != from_address:
        # formataddr probably got confused by special characters.
        mfrom = from_address
    return mfrom
