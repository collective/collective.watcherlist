from zope.interface import Attribute
from zope.interface import Interface


class IWatcherList(Interface):

    watchers = Attribute("Members waning to get changes via email")
    extra_addresses = Attribute("Extra email addresses")
    send_emails = Attribute("Send e-mails yes/no")

    def send(view_name, **kw):
        """Send mail to our addresses using browser view 'view_name'."""
