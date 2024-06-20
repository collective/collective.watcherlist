from Acquisition import aq_base
from Products.CMFPlone.tests.utils import MockMailHost
from Products.Five import fiveconfigure
from Products.MailHost.interfaces import IMailHost
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Testing import ZopeTestCase as ztc
from zope.component import getSiteManager

# Sample implementation:
import collective.watcherlist
import collective.watcherlist.sample
import doctest
import unittest


try:
    # Plone 5
    from plone.registry.interfaces import IRegistry
    from Products.CMFPlone.interfaces.controlpanel import IMailSchema
    from zope.component import getUtility
except ImportError:
    # Plone 4 and lower
    IMailSchema = None

try:
    from Zope2.App import zcml

    zcml  # pyflakes
except ImportError:
    from Products.Five import zcml
ptc.setupPloneSite()

OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE


class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            ztc.installPackage(collective.watcherlist)
            # Load sample config:
            zcml.load_config("", collective.watcherlist.sample)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


class FunctionalTestCase(TestCase, ptc.FunctionalTestCase):

    def _setup(self):
        ptc.PloneTestCase._setup(self)
        # Replace normal mailhost with mock mailhost
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost("MailHost")
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)
        # Make sure our mock mailhost does not give a mailhost_warning
        # in the overview-controlpanel.
        self.configure_mail_host("mock", "admin@example.com")

    def _clear(self, call_close_hook=0):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost), provided=IMailHost)
        ptc.PloneTestCase._clear(self)

    def get_smtp_host(self):
        if IMailSchema is None:
            # Plone 4
            return self.portal.MailHost.smtp_host
        else:
            # Plone 5.0 and higher
            registry = getUtility(IRegistry)
            mail_settings = registry.forInterface(
                IMailSchema, prefix="plone", check=False
            )
            return mail_settings.smtp_host

    def configure_mail_host(self, smtp_host, address=None):
        if IMailSchema is None:
            # Plone 4
            self.portal.MailHost.smtp_host = smtp_host
            if address is not None:
                self.portal.email_from_address = address
        else:
            # Plone 5.0 and higher
            registry = getUtility(IRegistry)
            mail_settings = registry.forInterface(
                IMailSchema, prefix="plone", check=False
            )
            if not isinstance(smtp_host, unicode):
                # must be unicode
                smtp_host = smtp_host.decode("utf-8")
            mail_settings.smtp_host = smtp_host
            if address is not None:
                if isinstance(address, unicode):
                    # must be ascii
                    address = address.encode("utf-8")
                mail_settings.email_from_address = address

    def afterSetUp(self):
        """Add some extra content and do some setup."""
        # We need to do this as Manager:
        self.setRoles(["Manager"])

        # Add some news items:
        sample_text = "<p>Have I got news for <em>you</em>!</p>"
        self.portal.news.invokeFactory(
            "News Item", "first", title="First News", text=sample_text
        )
        self.portal.news.invokeFactory(
            "News Item", "second", title="Second News", text=sample_text
        )

        # Set fullname and email address of test user:
        member = self.portal.portal_membership.getAuthenticatedMember()
        member.setMemberProperties(
            {"fullname": "Test User", "email": "testuser@example.com"}
        )

        # Add extra members:
        self.addMember("maurits", "Maurits van Rees", "maurits@example.com")
        self.addMember("reinout", "Reinout van Rees", "reinout@example.com")

        # Setup test browser:
        try:
            from Testing.testbrowser import Browser

            Browser  # pyflakes
        except ImportError:
            from Products.Five.testbrowser import Browser
        self.browser = Browser()
        self.browser.handleErrors = False
        self.browser.addHeader("Accept-Language", "en-US")
        self.portal.error_log._ignored_exceptions = ()

        # No more Manager:
        self.setRoles([])

    def addMember(self, username, fullname, email):
        self.portal.portal_membership.addMember(username, ptc.default_password, [], [])
        member = self.portal.portal_membership.getMemberById(username)
        member.setMemberProperties({"fullname": fullname, "email": email})

    def browser_login(self, user=None):
        if not user:
            user = ptc.default_user
        self.browser.open(self.portal.absolute_url() + "/login_form")
        self.browser.getLink("Log in").click()
        self.browser.getControl(name="__ac_name").value = user
        self.browser.getControl(name="__ac_password").value = ptc.default_password
        self.browser.getControl(name="submit").click()


def test_suite():
    return unittest.TestSuite(
        [
            ztc.FunctionalDocFileSuite(
                "newsletter.txt",
                package="collective.watcherlist.sample",
                test_class=FunctionalTestCase,
            ),
        ]
    )


if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
