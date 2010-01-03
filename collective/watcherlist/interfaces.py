from zope.interface import Attribute
from zope.interface import Interface


class IWatcherList(Interface):

    watchers = Attribute("Members waning to get changes via email")
    extra_addresses = Attribute("Extra email addresses")
    send_mails = Attribute("Send mails yes/no")


class IEmailSender(Interface):

    def send_mail(view_name, **kw):
        """Send e-mail.

        Lookup browser view 'view_name' and use that to get the plain
        text and or html and subject of the email.

        Extra keyword arguments are passed to the update method of
        that browser view.
        """
        pass
