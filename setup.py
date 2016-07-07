import os
from setuptools import setup, find_packages

readme = open('README.rst').read()
tests = open(os.path.join('collective', 'watcherlist', 'README.rst')).read()
changes = open("CHANGES.rst").read()

version = '2.1.dev0'

setup(
    name='collective.watcherlist',
    version=version,
    description="Send emails from Plone to interested members (watchers)",
    long_description=readme + "\n" + tests + "\n" + changes,
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='Plone notifications watching',
    author='Maurits van Rees',
    author_email='maurits@vanrees.org',
    url='https://github.com/collective/collective.watcherlist',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Products.CMFPlone',
        'setuptools',
    ],
    extras_require={
        'test': [
            'Products.PloneTestCase',
        ],
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
