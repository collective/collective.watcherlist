from collective.watcherlist.interfaces import IWatcherList


def mail_news(object, event):
    """Send an email when a news item is published.
    """
    if event.new_state.id == 'published':
        watchers = IWatcherList(object)
        watchers.send('newsitem-mail')


def mail_i18n(object, event):
    """Send an i18n email when an object gets 'i18n' in the title.

    A bit silly perhaps, but this tests mails in a different encoding.
    """
    if 'i18n' in object.Title():
        watchers = IWatcherList(object)
        watchers.send('i18n-mail')
