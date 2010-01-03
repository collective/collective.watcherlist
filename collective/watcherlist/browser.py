from zope.app.component.hooks import getSite
from Products.CMFPlone.utils import getSiteEncoding
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView


class BaseMail(BrowserView):
    """Base class for e-mails.

    Inherit from this and override the subject, plain and/or html
    properties.

    Has a few extra methods that may come in handy.
    """

    @property
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
        """Return safe unicode version of value, using our preferred charset.
        """
        charset = self.charset
        return safe_unicode(value, encoding=charset)

    @property
    def html(self):
        """The html version of the e-mail.
        """
        return u''

    @property
    def plain(self):
        """The plain text version of the e-mail.
        """
        return u''

    @property
    def subject(self):
        """The subject of the e-mail.
        """
        return u'[No subject]'

    def __call__(self):
        """Render the e-mail.

        You can use this to test the e-mail in the browser.  By
        default you see the html version.

        To view the subject, visit .../@@your-view?type=subject

        To view the plain text version, visit
        .../@@your-view?type=plain
        """
        type_ = self.request.get('type', '')
        if type_ == 'plain':
            return self.plain
        elif type_ == 'subject':
            return self.subject
        return self.html
