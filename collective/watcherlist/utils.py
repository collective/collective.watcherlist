from zope.app.component.hooks import getSite
from Products.CMFPlone.utils import getSiteEncoding
from Products.CMFPlone.utils import safe_unicode


def charset(self):
    """Character set to use for encoding the email.

    If encoding fails we will try some other encodings.  We hope
    to get utf-8 here always actually.
    """
    portal = getSite()
    charset = portal.getProperty('email_charset', '')
    if not charset:
        charset = getSiteEncoding()
    return charset


def su(self, value):
    """Return safe unicode version of value.
    """
    charset = self.charset()
    return safe_unicode(value, encoding=charset)
