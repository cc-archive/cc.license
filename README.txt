==========
cc.license
==========


Installation
============

The python-librdf Ubuntu package must be installed manually (NOT 
python-rdflib, though having it shouldn't break anything), as it 
is not available through PyPI.


# Preconditions
The author, or the licenser in case the author did a contractual transfer of rights, need to have the exclusive rights on the work. If the work has already been published under a public license, it can be uploaded by any third party, once more on another platform, by using a compatible license, and making reference and attribution to the original license (e.g. by referring the URL of the original license).



Developing
==========

cc.license is available via `git <http://git.or.cz/>`_.  To checkout a
copy of the code, just run::

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

