from zope.component import testing

import doctest
import unittest


OPTIONFLAGS = (
    doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE
)


def test_suite():
    return unittest.TestSuite(
        [
            # Unit tests
            doctest.DocFileSuite(
                "README.rst",
                package="collective.watcherlist",
                setUp=testing.setUp,
                tearDown=testing.tearDown,
                optionflags=OPTIONFLAGS,
            ),
            doctest.DocFileSuite(
                "cornercases.txt",
                package="collective.watcherlist.tests",
                setUp=testing.setUp,
                tearDown=testing.tearDown,
                optionflags=OPTIONFLAGS,
            ),
        ]
    )
