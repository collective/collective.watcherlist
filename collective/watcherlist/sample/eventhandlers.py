from collective.watcherlist.interfaces import IWatcherList


def mail_news(object, event):
    """Send an email when a news item is published.
    """
    if event.new_state.id == 'published':
        watchers = IWatcherList(object)
        watchers.send('newsitem-mail')
