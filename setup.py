from setuptools import setup, find_packages
import sys, os

setup(name='cc.license',
      version='0.03',
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
      data_files=[('cc/license/rdf', ['license.rdf/rdf/index.rdf',
                                      'license.rdf/rdf/selectors.rdf',
                                      'license.rdf/rdf/jurisdictions.rdf']),
                  ('cc/license/xml', ['license.rdf/xml/questions.xml'])],
      zip_safe=False,
      test_suite='nose.collector',
      install_requires=[
        'setuptools',
        'zope.interface',
        'nose',
        'Genshi',
        'lxml',
        'chameleon.zpt',
        'pylons', # XXX why does nose throw a RuntimeWarning without this?
        #'Babel',
        'FormEncode', # not sure why this is throwing a RuntimeWarning either
        'rdfadict',
        'enum',
      ],
      setup_requires=['setuptools-git',],
      entry_points="""
      # -*- Entry points: -*-
      [nose.plugins]
      pylons = pylons.test:PylonsPlugin 
      """,
      )
