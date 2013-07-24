from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from collective.watcherlist.i18n import _


watchingChoice = SimpleVocabulary([
        SimpleTerm('watch', 'watch', _(u'Add to wathers list')),
        SimpleTerm('unwatch', 'unwatch', _(u'Remove from watchers list')),
        ])
