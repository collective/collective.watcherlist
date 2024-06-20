from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from collective.watcherlist.i18n import _


watchingChoice = SimpleVocabulary(
    [
        SimpleTerm("watch", "watch", _("Add to watchers list")),
        SimpleTerm("unwatch", "unwatch", _("Remove from watchers list")),
    ]
)
