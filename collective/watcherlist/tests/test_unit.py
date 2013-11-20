import unittest

import doctest
from zope.component import testing

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        doctest.DocFileSuite(
            'README.rst', package='collective.watcherlist',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=OPTIONFLAGS),

        doctest.DocFileSuite(
            'cornercases.txt', package='collective.watcherlist.tests',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=OPTIONFLAGS),

    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
