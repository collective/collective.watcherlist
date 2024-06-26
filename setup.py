from setuptools import find_packages
from setuptools import setup

import os


readme = open("README.rst").read()
tests = open(os.path.join("collective", "watcherlist", "README.rst")).read()
changes = open("CHANGES.rst").read()

version = "4.0.0a1"

setup(
    name="collective.watcherlist",
    version=version,
    description="Send emails from Plone to interested members (watchers)",
    long_description=readme + "\n" + tests + "\n" + changes,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="Plone notifications watching",
    author="Maurits van Rees",
    author_email="maurits@vanrees.org",
    url="https://github.com/collective/collective.watcherlist",
    license="GPL",
    packages=find_packages(exclude=["ez_setup"]),
    namespace_packages=["collective"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Products.CMFPlone",
        "plone.api",
        "setuptools",
        "zope.formlib",
    ],
    python_requires=">=3.8, <4",
    extras_require={
        "test": [
            "plone.app.testing",
        ],
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
