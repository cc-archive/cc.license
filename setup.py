from setuptools import setup, find_packages

import sys
if sys.version_info < (3, 0):
    JINJA = [ 'jinja2']
if sys.version_info < (3, 6):
    # https://stackoverflow.com/questions/43163201/pyinstaller-syntax-error-yield-inside-async-function-python-3-5-1/43177028
    JINJA = [ 'jinja2==2.8.1' ]
else:
    JINJA = [ 'jinja2' ]

setup(name='cc.license',
      version='0.15.0',
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
          'rdflib',
          'cc.licenserdf',
          'setuptools',
          'nose',
          'lxml',
          'rdfadict',
          'cc.i18n',
          # Dependencies of dependencies
          # For pyRdfa3 - see their github repo README
          'html5lib<=0.95',
          # Moving from Python 2 to Python 3
          'future',
      ] + JINJA,

      dependency_links = [
          'https://github.com/creativecommons/cc.i18n/tarball/python3#egg=cc.i18n',
          'https://github.com/creativecommons/cc.licenserdf/tarball/python3#egg=cc.licenserdf',
          'https://github.com/creativecommons/rdfadict/tarball/python3#egg=rdfadict',
          # We don't use pyRdfa but our dependencies do, so we need this here
          'https://github.com/RDFLib/pyrdfa3/tarball/master#egg=pyRdfa',
      ],

      setup_requires=['setuptools-git',],
      )
