from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from Products.Five.browser import BrowserView

from collective.watcherlist import utils


class BaseMail(BrowserView):
    """Base class for e-mails.

    Inherit from this and override the subject, plain and/or html
    properties.

    Has a few extra methods that may come in handy.
    """

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

    def update(self, **kw):
        """Override this method to do something with the keyword arguments.
        """
        pass

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

    def prepare_email_message(self):
        plain = self.plain
        html = self.html

        # XXX We are currently sending plain text plus html here.  If
        # they are not both available, we could simplify the message.
        email_msg = MIMEMultipart('alternative')
        email_msg.epilogue = ''

        # We must choose the body charset manually.  Note that the
        # goal and effect of this loop is to determine the
        # body_charset.
        for body_charset in 'US-ASCII', utils.get_charset(), 'UTF-8':
            try:
                plain.encode(body_charset)
                html.encode(body_charset)
            except UnicodeError:
                pass
            else:
                break
        # Encoding should work now; let's replace errors just in case.
        plain.encode(body_charset, 'replace')
        html.encode(body_charset, 'xmlcharrefreplace')

        text_part = MIMEText(plain, 'plain', body_charset)
        email_msg.attach(text_part)

        html_part = MIMEText(html, 'html', body_charset)
        email_msg.attach(html_part)
        return email_msg
