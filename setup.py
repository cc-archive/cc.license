from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='cc.license',
      version=version,
      description="License selection based on ccREL-based metadata.",
      classifiers=[],
      keywords='',
      author='Creative Commons',
      author_email='software@creativecommons.org',
      url='http://wiki.creativecommons.org/CcLicense',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      install_requires=[
        'setuptools',
        'zope.interface',
        'nose',
        'Genshi',
      ],
      setup_requires=['setuptools-git',],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
