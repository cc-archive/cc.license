==========
cc.license
==========


Installation
============

The python-librdf package must be installed manually (NOT
python-rdflib, though having it shouldn't break anything), as it
is not available through PyPI.


Developing
==========

cc.license is available via git.  To checkout a
copy of the code, just run:

  $ git clone https://github.com/creativecommons/cc.license.git

To create an environment and install dependencies, run::

  $ cd cc.license
  $ virtualenv .
  $ . bin/activate
  $ python bootstrap.py

You should also create the .mo files that the cc.i18n module uses:

  $ bin/compile_mo

You can then run tests using:

  $ nosetests
