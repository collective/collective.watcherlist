try:
    from email.utils import parseaddr
    from email.utils import formataddr
except ImportError:
    # BBB for python2.4 if we want that.
    from email.Utils import parseaddr
    from email.Utils import formataddr

import logging
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import log_exc
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from smtplib import SMTPException
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter
import pkg_resources
import socket
import textwrap
from collective.watcherlist.interfaces import IWatcherList
from collective.watcherlist import utils

logger = logging.getLogger('collective.watcherlist')

wrapper = textwrap.TextWrapper(initial_indent='    ', subsequent_indent='    ')

zope2_egg = pkg_resources.working_set.find(
    pkg_resources.Requirement.parse('Zope2'))
if zope2_egg and (zope2_egg.parsed_version >=
                  pkg_resources.parse_version('2.12')):
    USE_SECURE_SEND = False
else:
    USE_SECURE_SEND = True


class EmailSender(object):

    def get_mail_host(self):
        """Get the MailHost object.

        Return None in case of problems.
        """
        portal = getSite()
        mail_host = getToolByName(portal, 'MailHost', None)
        if mail_host is None:
            return None

        request = portal.REQUEST
        ctrlOverview = getMultiAdapter((portal, request),
                                       name='overview-controlpanel')
        mail_settings_correct = not ctrlOverview.mailhost_warning()
        if not mail_settings_correct:
            return None
        return mail_host

    def get_mail_from_address(self):
        portal = getSite()
        from_address = portal.getProperty('email_from_address', '')
        from_name = portal.getProperty('email_from_name', '')
        mfrom = formataddr((from_name, from_address))
        if parseaddr(mfrom)[1] != from_address:
            # formataddr probably got confused by special characters.
            mfrom = from_address
        return mfrom

    def get_addresses(self, context):
        watcher_list = IWatcherList(context)
        if not watcher_list.send_mails:
            logger.info("send_mails is False so not getting addresses")
            return []
        addresses = watcher_list.addresses

        # Filter out empty e-mail addresses; for example in case
        # of LDAP users the email may not be known.  See:
        # http://plone.org/products/poi/issues/213
        # Also, we require unicode.
        filtered = [utils.su(a) for a in addresses if a]
        return filtered

    def get_email_content_and_subject(self, context, view_name, **kw):
        request = context.REQUEST
        mail_content = getMultiAdapter((context, request), name=view_name)
        if kw:
            mail_content.update(**kw)
        if hasattr(mail_content, 'subject'):
            subject = mail_content.subject
        else:
            subject = u''
        if hasattr(mail_content, 'plain'):
            plain = mail_content.plain
        else:
            plain = u''
        if hasattr(mail_content, 'html'):
            html = mail_content.html
        else:
            html = u''

        # XXX We are currently sending plain text plus html here.  If
        # they are not both available, we could simplify the message.

        email_msg = MIMEMultipart('alternative')
        email_msg.epilogue = ''

        # We must choose the body charset manually.  Note that the
        # goal and effect of this loop is to determine the
        # body_charset.
        for body_charset in 'US-ASCII', utils.charset(), 'UTF-8':
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
        return email_msg, subject

    def send_mail(self, context, view_name, **kw):
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
        mail_host = self.get_mail_host()
        if mail_host is None:
            logger.warn("Cannot send notification email: please configure "
                        "MailHost correctly.")
            return

        addresses = self.get_addresses(context)
        if not addresses:
            logger.info("No addresses found.")
            return
        email_msg, subject = self.get_email_content_and_subject(
            context, view_name, **kw)
        mfrom = self.get_mail_from_address()
        charset = utils.charset()

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
                    mail_host.secureSend(message=email_msg,
                                         mto=address,
                                         mfrom=mfrom,
                                         subject=subject,
                                         charset=charset)
                else:
                    # Make 'immediate' optional?
                    mail_host.send(message=email_msg,
                                   mto=address,
                                   mfrom=mfrom,
                                   subject=subject,
                                   immediate=True,
                                   charset=charset)
            except (socket.error, SMTPException), exc:
                log_exc(('Could not send email from %s to %s regarding issue '
                         'in tracker %s\ntext is:\n%s\n') % (
                        mfrom, address, context.absolute_url(), email_msg))
                log_exc("Reason: %s: %r" % (exc.__class__.__name__, str(exc)))
            except:
                raise
