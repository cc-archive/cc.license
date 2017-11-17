from setuptools import setup, find_packages

setup(name='cc.license',
      version='0.14.25',
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
        'python-gettext<2.0',
        'jinja2',
        'cc.i18n',
      ],

      dependency_links = [
        'https://github.com/creativecommons/cc.i18n/tarball/master#egg=cc.i18n',
        'https://github.com/creativecommons/cc.licenserdf/tarball/master#egg=cc.licenserdf',
      ],

      setup_requires=['setuptools-git',],
      )
