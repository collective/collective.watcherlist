from plone.app.contentrules.handlers import execute


def added(event):
    obj = event.object
    execute(obj, event)


def removed(event):
    obj = event.object
    execute(obj, event)


def toggle(event):
    obj = event.object
    execute(obj, event)
