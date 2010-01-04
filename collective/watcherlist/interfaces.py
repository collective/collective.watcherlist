from zope.interface import Attribute
from zope.interface import Interface


class IWatcherList(Interface):

    watchers = Attribute("Members waning to get changes via email")
    extra_addresses = Attribute("Extra email addresses")
    send_mails = Attribute("Send mails yes/no")
