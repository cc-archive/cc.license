==========
cc.license
==========


Installation
============

The python-librdf Ubuntu package must be installed manually (NOT 
python-rdflib, though having it shouldn't break anything), as it 
is not available through PyPI.


Developing
==========

cc.license is available via `git <http://git.or.cz/>`_.  To checkout a
copy of the code, copy,paste and just run::

  $ git clone git://code.creativecommons.org/cc.license

cc.license uses `zc.buildout <http://python.org/pypi/zc.buildout>`_ to
manage dependencies.  To bootstrap and install dependencies, run::

  $ cd cc.license
  $ python bootstrap.py
  $ ./bin/buildout

Once the buildout is complete a ``bin/python`` wrapper script will be
available which runs the Python interpreter with the dependencies and
development directory on the Python path.  You can use this
interpreter to run the test suite::

  $ ./bin/python setup.py nosetests

