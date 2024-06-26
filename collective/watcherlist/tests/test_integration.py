from plone import api
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import MOCK_MAILHOST_FIXTURE
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.textfield.value import RichTextValue
from plone.testing import layered
from plone.testing.zope import Browser

import collective.watcherlist
import collective.watcherlist.sample
import doctest
import unittest


class WatcherListLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=collective.watcherlist)
        self.loadZCML(package=collective.watcherlist.sample)

    def setUpPloneSite(self, portal):
        """Create some content and some users"""
        pw = api.portal.get_tool("portal_workflow")
        pw.setDefaultChain("simple_publication_workflow")

        with api.env.adopt_user("admin"):
            portal.invokeFactory(
                "Folder",
                "news",
                title="News",
            )
            api.content.transition(obj=portal.news, transition="publish")

            sample_text = "<p>Have I got news for <em>you</em>!</p>"
            portal.news.invokeFactory(
                "News Item",
                "first",
                title="First News",
                text=RichTextValue(
                    raw=sample_text,
                    mimeType="text/html",
                    outputMimeType="text/x-html-safe",
                ),
            )
            api.content.transition(obj=portal.news.first, transition="publish")

            portal.news.invokeFactory(
                "News Item",
                "second",
                title="Second News",
                text=RichTextValue(
                    raw=sample_text,
                    mimeType="text/html",
                    outputMimeType="text/x-html-safe",
                ),
            )
            api.content.transition(obj=portal.news.second, transition="publish")

            # Add extra members
            api.user.create(
                username="site_admin",
                email="site_admin@example.com",
                password=TEST_USER_PASSWORD,
                roles=["Site Administrator"],
                properties={"fullname": "Site Admin"},
            )

            api.user.create(
                username="maurits",
                email="maurits@example.com",
                password=TEST_USER_PASSWORD,
                properties={"fullname": "Maurits van Rees"},
            )
            api.user.create(
                username="reinout",
                email="reinout@example.com",
                password=TEST_USER_PASSWORD,
                properties={"fullname": "Reinout van Rees"},
            )


WATCHERLIST_FIXTURE = WatcherListLayer()
WATCHERLIST_INTEGRATION_TESTING = IntegrationTesting(
    bases=(WATCHERLIST_FIXTURE, MOCK_MAILHOST_FIXTURE),
    name="collective.watcherlist:Integration",
)
WATCHERLIST_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(WATCHERLIST_FIXTURE, MOCK_MAILHOST_FIXTURE),
    name="collective.watcherlist:Functional",
)


class TestMyView(unittest.TestCase):

    layer = WATCHERLIST_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def afterSetUp(self):
        """Add some extra content and do some setup."""
        # We need to do this as Manager:
        self.setRoles(["Manager"])

        self.browser = Browser()
        self.browser.handleErrors = False
        self.browser.addHeader("Accept-Language", "en-US")
        self.portal.error_log._ignored_exceptions = ()

        # No more Manager:
        self.setRoles([])

    def addMember(self, username, fullname, email):
        self.portal.portal_membership.addMember(username, TEST_USER_PASSWORD, [], [])
        member = self.portal.portal_membership.getMemberById(username)
        member.setMemberProperties({"fullname": fullname, "email": email})

    def browser_login(self, user=None):
        if not user:
            user = TEST_USER_ID
        self.browser.open(self.portal.absolute_url() + "/login_form")
        self.browser.getLink("Log in").click()
        self.browser.getControl(name="__ac_name").value = user
        self.browser.getControl(name="__ac_password").value = TEST_USER_PASSWORD
        self.browser.getControl(name="submit").click()


OPTIONFLAGS = (
    doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE
)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        layered(
            doctest.DocFileSuite(
                "newsletter.txt",
                package="collective.watcherlist.sample",
                optionflags=OPTIONFLAGS,
            ),
            layer=WATCHERLIST_FUNCTIONAL_TESTING,
        )
    )
    return suite
