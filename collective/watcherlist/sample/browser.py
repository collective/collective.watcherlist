from Acquisition import aq_inner
from collective.watcherlist.browser import BaseMail
from collective.watcherlist.interfaces import IWatcherList
from collective.watcherlist.utils import get_mail_host
from plone.app.textfield.value import RichTextValue
from plone.protect.interfaces import IDisableCSRFProtection
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from zope.component import getUtility
from zope.interface import alsoProvides


try:
    from plone.base.interfaces.controlpanel import IMailSchema
except ImportError:
    from Products.CMFPlone.interfaces.controlpanel import IMailSchema


class NewsItemMail(BaseMail):

    @property
    def subject(self):
        return "Newsflash: " + self.context.Title()

    @property
    def html(self):
        text = self.context.text
        if isinstance(text, RichTextValue):
            return text.output
        return text


class InternationalMail(BaseMail):

    @property
    def plain(self):
        # This says: Breaking international news
        return "Breaking \xefnt\xe9rn\xe4ti\xf3nal news: %s" % (self.context.Title())


class SubscriptionForm(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        watchers = IWatcherList(context)
        email = self.request.form.get("email")
        if email:
            watchers.watchers.append(email)
        if self.request.form.get("toggle"):
            watchers.toggle_watching()
        # Return the rendered form.
        return self.index()

    def is_watching(self):
        context = aq_inner(self.context)
        watchers = IWatcherList(context)
        return watchers.isWatching()


class SubscriptionOverview(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        watchers = IWatcherList(context)
        return "\n".join(watchers.addresses)


class MessagesView(BrowserView):
    """Show mailhost messages.

    I have trouble getting the tests to work.  portal.MailHost.messages
    is empty when I check it in newsletter.txt, but when I do it here in
    a browser view, it is filled.  So there is some mismatch between
    the database state that the testbrowser sees and outside of it.
    Anyway, this browser helps for that corner case.
    """

    def __call__(self):
        if "unconfigure" in self.request or "configure" in self.request:
            registry = getUtility(IRegistry)
            mail_settings = registry.forInterface(
                IMailSchema, prefix="plone", check=False
            )
            alsoProvides(self.request, IDisableCSRFProtection)
            if "unconfigure" in self.request:
                mail_settings.smtp_host = ""
                return "unconfigure"
            mail_settings.smtp_host = "localhost"
            return "configure"
        mailhost = get_mail_host()
        if "reset" in self.request:
            alsoProvides(self.request, IDisableCSRFProtection)
            mailhost.reset()
            return "reset"
        if "length" in self.request:
            # zero is easier to check for than 0, as that will give an empty string.
            return len(mailhost.messages) or "zero"
        if "message" in self.request:
            # one single message
            result = mailhost.messages[int(self.request["message"])]
            if isinstance(result, bytes):
                result = result.decode("utf-8")
            return result
        return mailhost.messages
