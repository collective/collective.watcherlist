import unittest

from zope.testing import doctest
from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

import collective.watcherlist
# Sample implementation:
import collective.watcherlist.sample


class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            ztc.installPackage(collective.watcherlist)
            # Load sample config:
            zcml.load_config('', collective.watcherlist.sample)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


class FunctionalTestCase(TestCase, ptc.FunctionalTestCase):

    def afterSetUp(self):
        """Add some extra content and do some setup.
        """
        # We need to do this as Manager:
        self.setRoles(['Manager'])

        # Add some news items:
        sample_text = "<p>Have I got news for <em>you</em>!</p>"
        self.portal.news.invokeFactory(
            'News Item', 'first', title="First News", text=sample_text)
        self.portal.news.invokeFactory(
            'News Item', 'second', title="Second News", text=sample_text)

        # Set fullname and email address of test user:
        member = self.portal.portal_membership.getAuthenticatedMember()
        member.setMemberProperties({'fullname': 'Test User',
                                    'email': 'testuser@example.com'})

        # Add extra members:
        self.addMember('maurits', 'Maurits van Rees', 'maurits@example.com')
        self.addMember('reinout', 'Reinout van Rees', 'reinout@example.com')

        # Setup test browser:
        from Products.Five.testbrowser import Browser
        self.browser = Browser()
        self.browser.handleErrors = False
        self.browser.addHeader('Accept-Language', 'en-US')
        self.portal.error_log._ignored_exceptions = ()

        # No more Manager:
        self.setRoles([])

    def addMember(self, username, fullname, email):
        self.portal.portal_membership.addMember(
            username, ptc.default_password, [], [])
        member = self.portal.portal_membership.getMemberById(username)
        member.setMemberProperties({'fullname': fullname, 'email': email})

    def browser_login(self, user=None):
        if not user:
            user = ptc.default_user
        self.browser.open(self.portal.absolute_url() + '/login_form')
        self.browser.getLink('Log in').click()
        self.browser.getControl(name='__ac_name').value = user
        self.browser.getControl(name='__ac_password').value = \
            ptc.default_password
        self.browser.getControl(name='submit').click()


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        doctestunit.DocFileSuite(
            'README.txt', package='collective.watcherlist',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=OPTIONFLAGS),

        #doctestunit.DocTestSuite(
        #    module='collective.watcherlist.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='collective.watcherlist',
        #    test_class=TestCase),

        ztc.FunctionalDocFileSuite(
            'newsletter.txt', package='collective.watcherlist.sample',
            test_class=FunctionalTestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
