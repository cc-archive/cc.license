from setuptools import setup, find_packages

setup(
    name='cc.license',
    description="License selection based on ccREL-based metadata.",
    version='0.14.25',
    url='http://wiki.creativecommons.org/CcLicense',
    license='MIT',
    author='Creative Commons',
    author_email='software@creativecommons.org',

    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    namespace_packages=['cc', ],
    test_suite='nose.collector',

    install_requires=[
        'cc.i18n',
        'cc.licenserdf',
        'jinja2',
        'lxml',
        'nose',
        'python-gettext',
        'rdfadict',
        'rdflib',
        'setuptools'],

    dependency_links=[
        'https://github.com/creativecommons/cc.i18n/tarball/'
        'master#egg=cc.i18n',
        'https://github.com/creativecommons/cc.licenserdf/tarball/'
        'master#egg=cc.licenserdf'],

    setup_requires=['setuptools-git', ],
    )
