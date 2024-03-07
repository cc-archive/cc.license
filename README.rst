==========
cc.license
==========

----

🛑 **As of 2023-09-27, this project was deprecated by the new CC Legal Tools**
(cc-legal-tools-app_, cc-legal-tools-data_).

.. _cc-legal-tools-app: https://github.com/creativecommons/cc-legal-tools-app
.. _cc-legal-tools-data: https://github.com/creativecommons/cc-legal-tools-data

----

Python app that runs part of the license engine on CC's website 


ccEngine
========

This repository is part of the ccEngine: `cc-archive/cc.engine`_.

.. _`cc-archive/cc.engine`: https://github.com/cc-archive/cc.engine


Installation
============

The python-librdf Ubuntu package must be installed manually (NOT 
python-rdflib, though having it shouldn't break anything), as it 
is not available through PyPI.


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

