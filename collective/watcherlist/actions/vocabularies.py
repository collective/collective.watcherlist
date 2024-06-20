from collective.watcherlist.i18n import _
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


watchingChoice = SimpleVocabulary(
    [
        SimpleTerm("watch", "watch", _("Add to watchers list")),
        SimpleTerm("unwatch", "unwatch", _("Remove from watchers list")),
    ]
)
