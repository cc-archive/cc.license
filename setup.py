from setuptools import setup, find_packages
import sys, os

setup(name='cc.license',
      version='0.14.8',
      namespace_packages = ['cc',],
      description="License selection based on ccREL-based metadata.",
      classifiers=[],
      keywords='',
      author='Creative Commons',
      author_email='software@creativecommons.org',
      url='http://wiki.creativecommons.org/CcLicense',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      #package_data={'cc.license': ['*.xml', '*.txt']}, # doesn't work
      zip_safe=False,
      test_suite='nose.collector',
      install_requires=[
        'rdflib<3.0',
        'cc.licenserdf',
        'setuptools',
        'nose',
        'lxml',
        'rdfadict',
        'python-gettext',
        'jinja2',
        'cc.i18n',
      ],
      setup_requires=['setuptools-git',],
      )
