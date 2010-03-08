=====
Tower
=====

Tower provides some additional functionality to Jinja and it's i18n extension,
and the Babel library.  Specifics:

- Pulls strings from a variety of sources: Python, JavaScript, and .lhtml files.
- Collapses whitespace in all strings to prevent unwieldy msgids.
- Supports Gettext context (msgctxt) in all gettext, and ngettext calls.
- Supports merging PHP and Python .pot files.  This is temporary.  If you want
  to support that for an extended time look at phppo2pypo in the `Translate Toolkit
  <http://translate.sourceforge.net/>`_.


Requirements
------------

Look at requirements.txt.


Installation
------------

`github <http://github.com/clouserw/tower>`_::

    pip install -e git://github.com/clouserw/tower.git#egg=tower

