import logging
from smtplib import SMTPException
import pkg_resources
import socket
from collective.watcherlist import utils

logger = logging.getLogger('collective.watcherlist')

zope2_egg = pkg_resources.working_set.find(
    pkg_resources.Requirement.parse('Zope2'))
if zope2_egg and (zope2_egg.parsed_version >=
                  pkg_resources.parse_version('2.12.3')):
    USE_SECURE_SEND = False
else:
    USE_SECURE_SEND = True


def simple_send_mail(message, addresses, subject, immediate=True):
    """Send a notification email to the list of addresses.

    The method is called 'simple' because all the clever stuff should
    already have been done by the caller.

    message is passed without change to the mail host.  It should
    probably be a correctly encoded Message or MIMEText.

    One mail with the given message and subject is sent for each address.

    Note that with Plone 4 (Zope 2.12) by default the sending is
    deferred to the end of the transaction.  This means an exception
    would roll back the transaction.  We usually do not want that, as
    the email sending is an extra: we do not mind too much if sending
    fails.  Luckily we have the option to send immediately, so we can
    catch and ignore exceptions.  In this method we do that.  You can
    override that by passing immediate=False.  Note that in Plone 3
    this has no effect at all.
    """
    mail_host = utils.get_mail_host()
    if mail_host is None:
        logger.warn("Cannot send notification email: please configure "
                    "MailHost correctly.")
        return

    mfrom = utils.get_mail_from_address()
    header_charset = utils.get_charset()

    for address in addresses:
        if not address:
            continue
        try:
            if USE_SECURE_SEND:
                mail_host.secureSend(message=message,
                                     mto=address,
                                     mfrom=mfrom,
                                     subject=subject,
                                     charset=header_charset)
            else:
                mail_host.send(message,
                               mto=address,
                               mfrom=mfrom,
                               subject=subject,
                               immediate=immediate,
                               charset=header_charset)
        except (socket.error, SMTPException):
            logger.warn('Could not send email to %s with subject %s',
                        address, subject)
        except:
            raise
