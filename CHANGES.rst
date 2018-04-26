Changelog
=========

3.0.2 (unreleased)
------------------

- Don't test with Plone 4.1, 4.2 or Python 2.6 anymore.
  It should still work, but I don't want to spend time fixing the build on Travis.
  [maurits]


3.0.1 (2018-04-26)
------------------

- Declare ``zope.formlib`` dependency.  [maurits]


3.0 (2016-12-23)
----------------

- Pass ``immediate=False`` by default.  This used to be ``True``.  The
  original idea was to send emails immediately, so that we could catch
  any errors ourselves and continue with a warning.  But since Plone
  4.1 the emails are by default sent at the end of the transaction,
  and exceptions are caught.  For immediate mails they are not caught
  there.  So for our uses cases it makes most sense to not send emails
  immediately, as then Plone does what we want already.  You can still
  pass ``immediate=True`` to ``mailer.simple_send_mail`` or now also
  to ``watchers.send`` if you want the old behavior back.
  This fixes `issue #8 <https://github.com/collective/collective.watcherlist/issues/8>`_.
  [maurits]

- Check ``allow_recursive`` on the watcher list.  The default value is
  true, which gives the same behavior as before.  When the value is
  false, the ``addresses`` property only looks for watchers on the
  current item, not on the parent.  A sample usage would be in
  Products.Poi to only allow recursive if an issue is not yet
  assigned.  (I am going to use this in custom code for a client).
  [maurits]

- Strip the email address that we get from a member or the site.
  I have a site where some email addresses are ``test@example.org\r\n``,
  which gives an error when sending.
  [maurits]


2.0 (2016-07-07)
----------------

- Removed backwards compatibility code for Plone 3.3 and 4.0.  We
  already were not testing on 3.3 anymore, and 4.0 is too hard to keep
  working too.  [maurits]

- Fixed Plone 5 email sending.  Improved code quality.  Fixed Travis tests.  [maurits]

- When the internal watchers list is of type list (instead of tuple),
  make sure its updated when toggling a watcher [skurfer]

1.2 (2013-12-03)
----------------

- Added events, triggers and action for content rules.  [Gagaro]


1.1 (2012-11-06)
----------------

- Made compatible with Plone 4.3 (keeping compatibility with Plone 3).
  [maurits]

- Moved to https://github.com/collective/collective.watcherlist
  [maurits]


1.0 (2012-04-21)
----------------

- When showing the plain text in the browser as test, force text/plain
  as content-type.
  [maurits]


0.3 (2011-05-09)
----------------

- Catch MailHostErrors when sending email.
  [maurits]


0.2 (2010-02-27)
----------------

- You can now add ``only_these_addresses`` as an argument to the send
  method.  This forces sending only to those addresses and ignoring
  all others.
  [maurits]

- Fixed possible UnicodeDecodeError when the plain text or html part
  of the email was not unicode.
  [maurits]


0.1 (2010-02-26)
----------------

- Initial release
