import os
from setuptools import setup, find_packages

readme = open('README.rst').read()
tests = open(os.path.join('collective', 'watcherlist', 'README.rst')).read()
changes = open("CHANGES.rst").read()

version = '1.2'

setup(
    name='collective.watcherlist',
    version=version,
    description="Send emails from Plone to interested members (watchers)",
    long_description=readme + "\n" + tests + "\n" + changes,
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 3.3",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
    ],
    keywords='',
    author='Maurits van Rees',
    author_email='maurits@vanrees.org',
    url='http://plone.org/products/collective.watcherlist',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Plone',
    ],
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
