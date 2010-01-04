import logging
from smtplib import SMTPException
import pkg_resources
import socket
from collective.watcherlist import utils

logger = logging.getLogger('collective.watcherlist')

zope2_egg = pkg_resources.working_set.find(
    pkg_resources.Requirement.parse('Zope2'))
if zope2_egg and (zope2_egg.parsed_version >=
                  pkg_resources.parse_version('2.12')):
    USE_SECURE_SEND = False
else:
    USE_SECURE_SEND = True


class EmailSender(object):

    def send_mail(self, message, addresses, subject):
        """Send a notification email to the list of addresses.

        context is the object about which an email should be sent.

        view_name is the browser view that will be used for sending.
        We are looking for attributes 'html' and 'plain'.

        Adapted from PoiTracker.

        XXX Note to self [maurits]: look at this blog post from Marius
        Gedminas, titled "Sending Unicode emails in Python":
        http://mg.pov.lt/blog/unicode-emails-in-python.html

        Some other interesting stuff:

        http://maurits.vanrees.org/weblog/archive/2009/09/international-emails

        http://plone.org/documentation/manual/upgrade-guide/version/upgrading-plone-3-x-to-4.0/updating-add-on-products-for-plone-4.0/mailhost.securesend-is-now-deprecated-use-send-instead

        """
        mail_host = utils.get_mail_host()
        if mail_host is None:
            logger.warn("Cannot send notification email: please configure "
                        "MailHost correctly.")
            return

        mfrom = utils.get_mail_from_address()
        charset = utils.get_charset()

        for address in addresses:
            # Perhaps offer to send one mail to all users,
            # probably in bcc then; we should have one general email
            # address in the To address then.
            #
            # Hm, but we may want to add a link at the bottom where they
            # can unsubscribe/unwatch this item, and for everyone that
            # could be a different link.  So never mind.

            try:
                # Note that charset is only used for the headers, not
                # for the body text as that is a Message/MIMEText
                # already.  Note also that we try to send immediately,
                # so we can catch and ignore exceptions.

                # Note that 'immediate' only works with Plone 4 (Zope
                # 2.12).  If we want to support Plone 3 we must use
                # secureSend.
                if USE_SECURE_SEND:
                    mail_host.secureSend(message=message,
                                         mto=address,
                                         mfrom=mfrom,
                                         subject=subject,
                                         charset=charset)
                else:
                    # Make 'immediate' optional?
                    mail_host.send(message=message,
                                   mto=address,
                                   mfrom=mfrom,
                                   subject=subject,
                                   immediate=True,
                                   charset=charset)
            except (socket.error, SMTPException):
                logger.warn('Could not send email to %s with subject %s',
                            address, subject)
            except:
                raise
