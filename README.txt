Introduction
============

``collective.watcherlist`` is a package that enables you to keep a
list of people who want to receive emails when an item gets updated.
The main use case is something like Products.Poi_, which is an issue
tracker for Plone.  That product lets you create an issue tracker.  In
this tracker people can add issues.  The tracker has managers.
Everytime a new issue is posted, the managers should receive an email.
When a manager responds to an issue, the original poster (and the
other managers) should get an email.  Anyone interested in following
the issue, should be able to add themselves to the list of people who
get an email.  The functionality for this was in Poi, but has now been
factored out into this ``collective.watcherlist`` package.


Who should use this package?
============================

This is not a package for end users.  Out of the box it does nothing.
It is a package for integrators or developers.  You need to write some
python and zcml in your own package (like Poi now does) to hook
``collective.watcherlist`` up in your code.

We gladly use the ZCA (Zope Component Architecture) to allow others to
register their own adapters and own email texts, so outside of Zope
the package does not make much sense.  And we import some code from
Plone too, so you will need that.  If you want to use it in bare Zope
or CMF, contact me: we can probably do some conditional imports
instead.

``collective.watcherlist`` might also be usable as a basis for a
newsletter product.  If you feel `Singing and Dancing`_ is overkill
for you, or too hard to adapt to your specific needs, you could try
writing some code around ``collective.watcherlist`` instead.


Basic integration steps
=======================

In its simplest form, the integration that is needed, is this:

- Register an adapter from your content type to
  ``collective.watcherlist.interfaces.IWatcherList``.  In a lot of
  cases using the default implementation as factory for this adapter
  is fine: ``collective.watcherlist.watchers.WatcherList``

- Create an html form where people can add themselves to the watcher
  list.  This could also be PloneFormGen_ form with a custom script
  adapter as action.

- Register a BrowserView for your content type, inheriting from
  ``collective.watcherlist.browser.BaseMail`` and override its
  properties ``subject``, ``plain`` and/or ``html``.

- Create an event handler or some other code that gets the adapter for
  your content type and uses that to send an email with the subject
  and contents defined in the browser view you created.

Credits
=======

People
------

* Maurits van Rees [maurits] <maurits@vanrees.org> author

Companies
---------

* Zest Software http://zestsoftware.nl/
