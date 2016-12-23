from collective.watcherlist import utils
import logging


logger = logging.getLogger('collective.watcherlist')


def simple_send_mail(message, addresses, subject, immediate=False):
    """Send a notification email to the list of addresses.

    The method is called 'simple' because all the clever stuff should
    already have been done by the caller.

    message is passed without change to the mail host.  It should
    probably be a correctly encoded Message or MIMEText.

    One mail with the given message and subject is sent for each address.

    Starting with Plone 4 (Zope 2.12) by default the sending is deferred
    to the end of the transaction.  It seemed that this would mean that
    an exception during sending would roll back the transaction, so we
    passed immediate=True by default, catching the error and continuing.

    But this is not the case: Products/CMFPlone/patches/sendmail.py
    patches the email sending to not raise an error when the transaction
    is already finished.  So in case of problems the transaction is not
    rolled back.  (zope.sendmail 4.0 does this itself.)

    And that is fine for us: usually a problem with sending the email
    should not result in a transaction rollback or an error for the
    user.

    There is still the option to send immediately.  If you want this,
    you can pass immediate=False to this function.
    """
    mail_host = utils.get_mail_host()
    if mail_host is None:
        logger.warn("Cannot send notification email: please configure "
                    "MailHost correctly.")
        # We print some info, which is perfect for checking in unit
        # tests.
        print 'Subject =', subject
        print 'Addresses =', addresses
        print 'Message ='
        print message
        return

    mfrom = utils.get_mail_from_address()
    header_charset = utils.get_charset()

    for address in addresses:
        if not address:
            continue
        mail_host.send(
            message,
            mto=address,
            mfrom=mfrom,
            subject=subject,
            immediate=immediate,
            charset=header_charset)
