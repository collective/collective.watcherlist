import os
from setuptools import setup, find_packages

readme = open(os.path.join('collective', 'watcherlist', 'README.txt')).read()

version = '1.1.dev0'

setup(name='collective.watcherlist',
      version=version,
      description="Send emails from Plone to interested members (watchers)",
      long_description=readme + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 3.3",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
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
