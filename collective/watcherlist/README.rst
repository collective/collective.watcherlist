collective.watcherlist
======================

Sample integration
------------------

Let's give an example of what you need to do in your own code to use
this package.  We define a class that holds some info about a party::

  >>> class Party(object):
  ...     def __init__(self, reason):
  ...         self.reason = reason
  ...         self.invited = []

We tell the ZCA how to adapt a Party to a watcher list: how to turn it
into an object that holds a list of interested people and knows how to
send them an email.  Normally you would define an interface
``IParty``, say that the ``Party`` class implements it and use zcml to
register an adapter for that, something like this::

  <adapter
      for=".interfaces.IParty"
      factory="collective.watcherlist.watchers.WatcherList"
      />

Let's ignore the interface and use python (as that is a bit easier to
use in tests).  We will use the default implementation of a
watcherlist as provided by the package::

  >>> from zope.component import getGlobalSiteManager
  >>> from collective.watcherlist.watchers import WatcherList
  >>> sm = getGlobalSiteManager()
  >>> sm.registerAdapter(WatcherList, (Party, ))

.. This documentation doubles as automated test, so we run into a test
.. detail here: the WatcherList adapter stores the watchers in an
.. annotation, so we need to tell the ZCA how to do that; for standard
.. Plone/Archetypes content types this is already done, so you usually do
.. not need to care about this.  Oh, we can hide this, nice::
  :hide:

  >>> from zope.annotation.interfaces import IAnnotations
  >>> from zope.annotation.attribute import AttributeAnnotations
  >>> sm.registerAdapter(AttributeAnnotations, (Party, ), IAnnotations)

Now we create a Party and invite people::

  >>> birthday = Party("Maurits' birthday")
  >>> birthday.invited.append('Fred')
  >>> birthday.invited.append('Mirella')

We see if we can get a watcherlist for it::

  >>> from collective.watcherlist.interfaces import IWatcherList
  >>> watcherlist = IWatcherList(birthday)
  >>> watcherlist
  <collective.watcherlist.watchers.WatcherList object at ...>

We can ask several things of this list::

  >>> watcherlist.watchers
  []
  >>> watcherlist.send_emails
  True
  >>> watcherlist.addresses
  ()

We can add watchers.  These should be email addresses or (at least in
a Plone context) the ids of members in the site.  In your package you
would either create a button or other small form that people can use
to add themselves to the list, or create some code that automatically
adds some people, as Poi does for the creator of a new issue.  The
code is simple::

  >>> watcherlist.watchers.append('maurits@example.org')
  >>> watcherlist.watchers.append('reinout@example.org')
  >>> watcherlist.watchers
  ['maurits@example.org', 'reinout@example.org']
  >>> watcherlist.addresses
  ('maurits@example.org', 'reinout@example.org')

You can always switch off email sending.  This has the effect that no
addresses are reported::

  >>> watcherlist.send_emails = False
  >>> watcherlist.watchers
  ['maurits@example.org', 'reinout@example.org']
  >>> watcherlist.addresses
  ()

Undo that::

  >>> watcherlist.send_emails = True
  >>> watcherlist.watchers
  ['maurits@example.org', 'reinout@example.org']
  >>> watcherlist.addresses
  ('maurits@example.org', 'reinout@example.org')

Now we send an email.  We get the email text and subject simply from a
browser view that we define.  In the test this means we need to give
the Party a request object::

  >>> from zope.publisher.browser import TestRequest
  >>> birthday.REQUEST = TestRequest()

We now send an invitation email, but this fails::

  >>> watcherlist.send('invitation')
  Traceback (most recent call last):
  ...
  ComponentLookupError...

This means we need to create a browser view with that name.  As the
basis we should take the base browser view defined in the
``collective.watcherlist`` package.  It contains three properties that
you would normally override: subject, plain and html::

  >>> from collective.watcherlist.browser import BaseMail
  >>> class PartyMail(BaseMail):
  ...     @property
  ...     def subject(self):
  ...         return self.context.reason
  ...     @property
  ...     def plain(self):
  ...         return "Invited are %s" % self.context.invited
  ...     @property
  ...     def html(self):
  ...         return "<p>%s</p>" % self.plain

You would normally register this with zcml, just like any other
browser view.  But here we do that in python code::

  >>> from zope.interface import Interface
  >>> sm.registerAdapter(PartyMail, (Party, TestRequest), Interface, 'invitation')

And we send the invitation again, in both plain text and html.  In
this test we have no proper mail host setup, so we simply print the
relevant info so we can see what would happen::

  >>> watcherlist.send('invitation')
  Subject = Maurits' birthday
  Addresses = ('maurits@example.org', 'reinout@example.org')
  Message =
  From...
  Content-Type: multipart/alternative;...
  ...
  Content-Type: text/plain; charset="us-ascii"
  ...
  Invited are ['Fred', 'Mirella']
  ...
  Content-Type: text/html; charset="us-ascii"
  ...
  <p>Invited are ['Fred', 'Mirella']</p>
  ...

Let's skip the html and see if that simplifies the mail::

  >>> PartyMail.html = ''
  >>> watcherlist.send('invitation')
  Subject = Maurits' birthday
  Addresses = ('maurits@example.org', 'reinout@example.org')
  Message =
  From...
  MIME-Version: 1.0
  Content-Type: text/plain; charset="us-ascii"
  Content-Transfer-Encoding: 7bit
  <BLANKLINE>
  Invited are ['Fred', 'Mirella']

If there is neither plain text nor html, we do not send anything::

  >>> PartyMail.plain = ''
  >>> watcherlist.send('invitation')

Let's add a bit of html again to see that only html goes fine too::

  >>> PartyMail.html = '<p>You are invited.</p>'
  >>> watcherlist.send('invitation')
  Subject = Maurits' birthday
  Addresses = ('maurits@example.org', 'reinout@example.org')
  Message =
  From...
  MIME-Version: 1.0
  Content-Type: text/html; charset="us-ascii"
  Content-Transfer-Encoding: 7bit
  <BLANKLINE>
  <p>You are invited.</p>

If we switch off email sending for this watcherlist... no emails are sent::

  >>> watcherlist.send_emails = False
  >>> watcherlist.send('invitation')

Reset that::

  >>> watcherlist.send_emails = True

Look at Products.Poi_ for some more examples of what you can do.

.. _Products.Poi: http://plone.org/products/poi
.. _`Singing and Dancing`: http://plone.org/products/dancing
.. _PloneFormGen: http://plone.org/products/ploneformgen
