import os
import base64
import shutil
from cStringIO import StringIO

from django.utils import translation

import jingo
from jingo.tests.test_helpers import render

from nose import with_setup
from nose.tools import eq_

import tower
from tower.tests.helpers import fake_extract_from_dir
from tower import ugettext as _, ungettext as n_
from tower import ugettext_lazy as _lazy, ungettext_lazy as n_lazy
from tower.management.commands.extract import create_pofile_from_babel

# Used for the _lazy() tests
_lazy_strings = {}
_lazy_strings['nocontext'] = _lazy('this is a test')
_lazy_strings['context'] = _lazy('What time is it?', 'context_one')

n_lazy_strings = {}
n_lazy_strings['s_nocontext'] = n_lazy('one light !', 'many lights !', 1)
n_lazy_strings['p_nocontext'] = n_lazy('one light !', 'many lights !', 3)
n_lazy_strings['s_context'] = n_lazy('%d poodle please', '%d poodles please',
                                     1, 'context_one')
n_lazy_strings['p_context'] = n_lazy('%d poodle please', '%d poodles please',
                                     3, 'context_one')


def setup():
    tower.activate('xx')

def setup_yy():
    tower.activate('yy')

def teardown():
    tower.deactivate_all()


@with_setup(setup, teardown)
def test_ugettext():
    # No context
    a_text = " this\t\r\n\nis    a\ntest  \n\n\n"
    p_text = "you ran a test!"
    eq_(p_text, _(a_text))

    # With a context
    a_text = "\n\tWhat time \r\nis it?  \n"
    p_text_1 = "What time is it? (context=1)"
    p_text_2 = "What time is it? (context=2)"
    eq_(p_text_1, _(a_text, 'context_one'))
    eq_(p_text_2, _(a_text, 'context_two'))


@with_setup(setup, teardown)
def test_ugettext_not_found():
    eq_('yo', _('yo'))
    eq_('yo yo', _('  yo  yo  '))
    eq_('yo', _('yo', 'context'))
    eq_('yo yo', _('  yo  yo  ', 'context'))


@with_setup(setup, teardown)
def test_ungettext():
    # No context
    a_singular = " one\t\r\n\nlight \n\n!\n"
    a_plural = " many\t\r\n\nlights \n\n!\n"
    p_singular = "you found a light!"
    p_plural = "you found a pile of lights!"
    eq_(p_singular, n_(a_singular, a_plural, 1))
    eq_(p_plural, n_(a_singular, a_plural, 3))

    # With a context
    a_singular = "%d \n\n\tpoodle please"
    a_plural = "%d poodles\n\n\t please\n\n\n"
    p_singular_1 = "%d poodle (context=1)"
    p_plural_1 = "%d poodles (context=1)"
    p_singular_2 = "%d poodle (context=2)"
    p_plural_2 = "%d poodles (context=2)"
    eq_(p_singular_1, n_(a_singular, a_plural, 1, 'context_one'))
    eq_(p_plural_1, n_(a_singular, a_plural, 3, 'context_one'))
    eq_(p_singular_2, n_(a_singular, a_plural, 1, 'context_two'))
    eq_(p_plural_2, n_(a_singular, a_plural, 3, 'context_two'))


@with_setup(setup, teardown)
def test_ungettext_not_found():
    eq_('yo', n_('yo', 'yos', 1, 'context'))
    eq_('yo yo', n_('  yo  yo  ', 'yos', 1, 'context'))
    eq_('yos', n_('yo', 'yos', 3, 'context'))
    eq_('yo yos', n_('yo', '  yo  yos  ', 3, 'context'))


@with_setup(setup, teardown)
def test_ugettext_lazy():
    eq_(unicode(_lazy_strings['nocontext']), 'you ran a test!')
    eq_(unicode(_lazy_strings['context']), 'What time is it? (context=1)')


@with_setup(setup, teardown)
def test_ungettext_lazy():
    eq_(unicode(n_lazy_strings['s_nocontext']), 'you found a light!')
    eq_(unicode(n_lazy_strings['p_nocontext']), 'you found a pile of lights!')
    eq_(unicode(n_lazy_strings['s_context']), '%d poodle (context=1)')
    eq_(unicode(n_lazy_strings['p_context']), '%d poodles (context=1)')


def test_add_context():
    eq_("nacho\x04testo", tower.add_context("nacho", "testo"))


def test_split_context():
    eq_(["", u"testo"], tower.split_context("testo"))
    eq_([u"nacho", u"testo"], tower.split_context("nacho\x04testo"))


def test_activate():
    tower.deactivate_all()
    tower.activate('xx')
    eq_(_('this is a test'), 'you ran a test!')
    tower.deactivate_all()


def test_cached_activate():
    """
    Make sure the locale is always activated properly, even when we hit a
    cached version.
    """
    tower.deactivate_all()
    tower.activate('fr')
    eq_(translation.get_language(), 'fr')
    tower.activate('fa')
    eq_(translation.get_language(), 'fa')
    tower.activate('fr')
    eq_(translation.get_language(), 'fr')
    tower.activate('de')
    eq_(translation.get_language(), 'de')
    tower.activate('fr')
    eq_(translation.get_language(), 'fr')
    tower.activate('fa')
    eq_(translation.get_language(), 'fa')


@with_setup(setup, teardown)
def test_template_simple():
    s = '{% trans %}this is a test{% endtrans %}'
    eq_(render(s), 'you ran a test!')

    s = '''{% trans %}
        this
        is
        a
        test
        {% endtrans %}'''
    eq_(render(s), 'you ran a test!')


@with_setup(setup, teardown)
def test_template_substitution():
    s = '{% trans user="wenzel" %} Hello {{ user }}{% endtrans %}'
    eq_(render(s), 'Hola wenzel')

    s = '''{% trans user="wenzel" %}
            Hello
            \t\r\n
            {{ user }}
            {% endtrans %}'''
    eq_(render(s), 'Hola wenzel')

@with_setup(setup, teardown)
def test_template_substitution_with_pluralization():
    s = '''{% trans count=1 %}
                one light !
            {% pluralize %}
                many lights !
            {% endtrans %}'''
    eq_(render(s), 'you found a light!')

    s = '''{% trans count=8 %}
                one light !
            {% pluralize %}
                many lights !
            {% endtrans %}'''
    eq_(render(s), 'you found a pile of lights!')


@with_setup(setup_yy, teardown)
def test_template_substitution_with_many_plural_forms():
    s = '''{% trans count=1 %}
                There is {{ count }} monkey.
            {% pluralize %}
                There are {{ count }} monkeys.
            {% endtrans %}'''
    eq_(render(s), 'Monkey count: 1 (Plural: 0)')

    s = '''{% trans count=3 %}
                There is {{ count }} monkey.
            {% pluralize %}
                There are {{ count }} monkeys.
            {% endtrans %}'''
    eq_(render(s), 'Monkey count: 3 (Plural: 1)')

    s = '''{% trans count=5 %}
                There is {{ count }} monkey.
            {% pluralize %}
                There are {{ count }} monkeys.
            {% endtrans %}'''
    eq_(render(s), 'Monkey count: 5 (Plural: 2)')


@with_setup(setup, teardown)
def test_template_gettext_functions():
    s = '{{ _("yy", "context") }}'
    eq_(render(s), 'yy')

    s = '{{ gettext("yy", "context") }}'
    eq_(render(s), 'yy')

    s = '{{ ngettext("1", "2", 1, "context") }}'
    eq_(render(s), '1')


def test_extract_tower_python():
    fileobj = StringIO(TEST_PO_INPUT)
    method = 'tower.management.commands.extract.extract_tower_python'
    output = fake_extract_from_dir(filename="filename", fileobj=fileobj,
                                   method=method)

    # god help you if these are ever unequal
    eq_(TEST_PO_OUTPUT, unicode(create_pofile_from_babel(output)))


def test_extract_tower_template():
    fileobj = StringIO(TEST_TEMPLATE_INPUT)
    method = 'tower.management.commands.extract.extract_tower_template'
    output = fake_extract_from_dir(filename="filename", fileobj=fileobj,
                                   method=method)

    # god help you if these are ever unequal
    eq_(TEST_TEMPLATE_OUTPUT, unicode(create_pofile_from_babel(output)))


TEST_PO_INPUT = """
# Make sure multiple contexts stay separate
_('fligtar')
_('fligtar', 'atwork')
_('fligtar', 'athome')

# Test regular plural form, no context
ngettext('a fligtar', 'many fligtars', 3)

# Make sure several uses collapses to one
ngettext('a fligtar', 'many fligtars', 1, 'aticecreamshop')
ngettext('a fligtar', 'many fligtars', 3, 'aticecreamshop')
ngettext('a fligtar', 'many fligtars', 5, 'aticecreamshop')

# Test comments
# L10n: Turn up the volume
_('fligtar    \n\n\r\t  talking')

# Test comments w/ plural and context
# L10n: Turn down the volume
ngettext('fligtar', 'many fligtars', 5, 'aticecreamshop')

# Test lazy strings are extracted
_lazy('a lazy string')
"""

TEST_PO_OUTPUT = """\
#: filename:3
msgid "fligtar"
msgstr ""

#: filename:4
msgctxt "atwork"
msgid "fligtar"
msgstr ""

#: filename:5
msgctxt "athome"
msgid "fligtar"
msgstr ""

#: filename:8
msgid "a fligtar"
msgid_plural "many fligtars"
msgstr[0] ""
msgstr[1] ""

#: filename:11
#: filename:12
#: filename:13
msgctxt "aticecreamshop"
msgid "a fligtar"
msgid_plural "many fligtars"
msgstr[0] ""
msgstr[1] ""

#. L10n: Turn down the volume
#: filename:23
msgctxt "aticecreamshop"
msgid "fligtar"
msgid_plural "many fligtars"
msgstr[0] ""
msgstr[1] ""

#: filename:26
msgid "a lazy string"
msgstr ""
"""

TEST_TEMPLATE_INPUT = """
  {{ _('sunshine') }}
  {{ _('sunshine', 'nothere') }}
  {{ _('sunshine', 'outside') }}

  {# Regular comment, regular gettext #}
  {% trans %}
    I like pie.
  {% endtrans %}

  {# L10n: How many hours? #}
  {% trans plural=4, count=4 %}
    {{ count }} hour left
  {% pluralize %}
    {{ count }} hours left
  {% endtrans %}

  {{ ngettext("one", "many", 5) }}

  {# L10n: This string has a hat. #}
  {% trans %}
  Let me tell you about a string
  who spanned
  multiple lines.
  {% endtrans %}
"""

TEST_TEMPLATE_OUTPUT = """\
#: filename:2
msgid "sunshine"
msgstr ""

#: filename:3
msgctxt "nothere"
msgid "sunshine"
msgstr ""

#: filename:4
msgctxt "outside"
msgid "sunshine"
msgstr ""

#: filename:7
msgid "I like pie."
msgstr ""

#. How many hours?
#: filename:12
msgid "%(count)s hour left"
msgid_plural "%(count)s hours left"
msgstr[0] ""
msgstr[1] ""

#: filename:18
msgid "one"
msgid_plural "many"
msgstr[0] ""
msgstr[1] ""

#. This string has a hat.
#: filename:21
msgid "Let me tell you about a string who spanned multiple lines."
msgstr ""
"""
