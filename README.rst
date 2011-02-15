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


A note on ``safe``-ness
-----------------------

L10n strings are marked "safe" for Jinja2 automatically, so they will not be
HTML-escaped::

    {{ _('Hello <strong>World</strong>') }}

This works as expected. When interpolating into an L10n string, however, it will
be marked as "unsafe" and escaped, unless you use `jingo's
<https://github.com/jbalogh/jingo/>`_ ``|fe()`` helper (which will escape the
arguments but not the string they are interpolated into). Like this::

    {{ _('Hello <strong>{0}</strong>')|fe(user.nickname) }}
