Changelog
=========

1.2 (2013-12-03)
----------------

- Nothing changed yet.


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
