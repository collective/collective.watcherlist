try:
    from email.utils import parseaddr
    from email.utils import formataddr
except ImportError:
    # BBB for python2.4 if we want that.
    from email.Utils import parseaddr
    from email.Utils import formataddr

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getSiteEncoding
from Products.CMFPlone.utils import log
from Products.CMFPlone.utils import log_exc
from Products.CMFPlone.utils import safe_unicode
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from smtplib import SMTPException
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter
import pkg_resources
import socket
import textwrap
from collective.watcherlist.interfaces import IWatcherList

wrapper = textwrap.TextWrapper(initial_indent='    ', subsequent_indent='    ')

zope2_egg = pkg_resources.working_set.find(
    pkg_resources.Requirement.parse('Zope2'))
if zope2_egg and (zope2_egg.parsed_version >=
                  pkg_resources.parse_version('2.12')):
    USE_SECURE_SEND = False
else:
    USE_SECURE_SEND = True


class EmailSender(object):

    def __init__(self, context):
        self.context = context

    @property
    def charset(self):
        """Character set to use for encoding the email.

        If encoding fails we will try some other encodings.  We hope
        to get utf-8 here always actually.
        """
        portal = getSite()
        charset = portal.getProperty('email_charset', '')
        if not charset:
            charset = getSiteEncoding()
        return charset

    def su(self, value):
        """Return safe unicode version of value.
        """
        charset = self.charset
        return safe_unicode(value, encoding=charset)

    def send_mail(self, view_name, **kw):
        """Send a notification email to the list of addresses.

        view_name is the browser view that will be used for sending.
        We are looking for attributes 'html' and 'plain'.

        Taken from PoiTracker.

        XXX Note to self [maurits]: look at this blog post from Marius
        Gedminas, titled "Sending Unicode emails in Python":
        http://mg.pov.lt/blog/unicode-emails-in-python.html

        Some other interesting stuff:

        http://maurits.vanrees.org/weblog/archive/2009/09/international-emails

        http://plone.org/documentation/manual/upgrade-guide/version/upgrading-plone-3-x-to-4.0/updating-add-on-products-for-plone-4.0/mailhost.securesend-is-now-deprecated-use-send-instead

        """
        context = aq_inner(self.context)
        request = context.REQUEST
        ctrlOverview = getMultiAdapter((context, request),
                                       name='overview-controlpanel')
        mail_settings_correct = not ctrlOverview.mailhost_warning()
        if not mail_settings_correct:
            log("Cannot send notification email: MailHost settings not "
                "correct.")
            return

        watcher_list = IWatcherList(context)
        addresses = watcher_list.addresses
        if not watcher_list.send_mails or not addresses:
            return

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

        portal = getSite()
        mailHost = getToolByName(portal, 'MailHost')
        charset = self.charset
        from_address = portal.getProperty('email_from_address', '')
        from_name = portal.getProperty('email_from_name', '')
        mfrom = formataddr((from_name, from_address))
        if parseaddr(mfrom)[1] != from_address:
            # formataddr probably got confused by special characters.
            mfrom = from_address


        # XXX We are currently sending plain text plus html here.  If
        # they are not both available, we could simplify the message.

        email_msg = MIMEMultipart('alternative')
        email_msg.epilogue = ''

        # We must choose the body charset manually.  Note that the
        # main goal and effect of this loop is to set the
        # body_charset.
        for body_charset in 'US-ASCII', charset, 'UTF-8':
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

        for address in addresses:
            # Perhaps offer to send one mail to all users,
            # probably in bcc then; we should have one general email
            # address in the To address then.
            #
            # Hm, but we want to add a link at the bottom where they
            # can unsubscribe/unwatch this item, and for everyone that
            # could be a different link.  So never mind.

            address = self.su(address)
            if not address:
                # E-mail address may not be known, for example in case
                # of LDAP users.  See:
                # http://plone.org/products/poi/issues/213
                # But this address should not be in the list then...
                continue
            try:
                # Note that charset is only used for the headers, not
                # for the body text as that is a Message/MIMEText
                # already.  Note also that we try to send immediately,
                # so we can catch and ignore exceptions.

                # Note that 'immediate' only works with Plone 4 (Zope
                # 2.12).  If we want to support Plone 3 we must use
                # secureSend.
                if USE_SECURE_SEND:
                    mailHost.secureSend(message=email_msg,
                                        mto=address,
                                        mfrom=mfrom,
                                        subject=subject,
                                        charset=charset)
                else:
                    # Make 'immediate' optional?
                    mailHost.send(message=email_msg,
                                  mto=address,
                                  mfrom=mfrom,
                                  subject=subject,
                                  immediate=True,
                                  charset=charset)
            except (socket.error, SMTPException), exc:
                log_exc(('Could not send email from %s to %s regarding issue '
                         'in tracker %s\ntext is:\n%s\n') % (
                        mfrom, address, self.absolute_url(), email_msg))
                log_exc("Reason: %s: %r" % (exc.__class__.__name__, str(exc)))
            except:
                raise
