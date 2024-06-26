from collective.watcherlist import utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Products.Five.browser import BrowserView


class BaseMail(BrowserView):
    """Base class for e-mails.

    Inherit from this and override the subject, plain and/or html
    properties.

    Has a few extra methods that may come in handy.
    """

    @property
    def html(self):
        """The html version of the e-mail."""
        return ""

    @property
    def plain(self):
        """The plain text version of the e-mail."""
        return ""

    @property
    def subject(self):
        """The subject of the e-mail."""
        return "[No subject]"

    def update(self, **kw):
        """Override this method to do something with the keyword arguments."""
        pass

    def __call__(self):
        """Render the e-mail.

        You can use this to test the e-mail in the browser.  By
        default you see the html version.

        To view the subject, visit .../@@your-view?type=subject

        To view the plain text version, visit
        .../@@your-view?type=plain
        """
        type_ = self.request.get("type", "")
        if type_ == "plain":
            # This may be a page template, but we want it to be
            # visible as plain text in the browser always.
            self.request.response.setHeader("content-type", "text/plain")
            return self.plain
        elif type_ == "subject":
            return self.subject
        return self.html

    def prepare_email_message(self):
        plain = self.plain
        html = self.html
        if not plain and not html:
            return None

        # We definitely want unicode at this point.
        plain = utils.su(plain)
        html = utils.su(html)

        # We must choose the body charset manually.  Note that the
        # goal and effect of this loop is to determine the
        # body_charset.
        for body_charset in "US-ASCII", utils.get_charset(), "UTF-8":
            try:
                plain.encode(body_charset)
                html.encode(body_charset)
            except UnicodeEncodeError:
                pass
            else:
                break
        # Encoding should work now; let's replace errors just in case.
        plain = plain.encode(body_charset, "replace")
        html = html.encode(body_charset, "xmlcharrefreplace")

        text_part = MIMEText(plain, "plain", body_charset)
        html_part = MIMEText(html, "html", body_charset)

        # No sense in sending plain text and html when we only have
        # one of those:
        if not plain:
            return html_part
        if not html:
            return text_part

        # Okay, we send both plain text and html
        email_msg = MIMEMultipart("alternative")
        email_msg.epilogue = ""
        email_msg.attach(text_part)
        email_msg.attach(html_part)
        return email_msg
