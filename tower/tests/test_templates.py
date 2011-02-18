import jingo
from jingo.tests.test_helpers import render
import jinja2
from test_utils import eq_


def test_safe():
    """Ensure _() calls won't be escaped by Jinja2."""
    txt = '<strong>Hello</strong>'
    rendered = render('{{ _("%s") }}' % txt)
    eq_(rendered, txt)


def test_interpolation_nonsafe():
    """Ensure '_() % something' is not safe."""
    tpl = '{{ _("Hello %s") % "<p>" }}'
    rendered = render(tpl)
    eq_(rendered, 'Hello &lt;p&gt;')


def test_format_nonsafe():
    """Ensure '_()|f(something)' is not safe."""
    tpl = '{{ _("Hello {0}")|f("<p>") }}'
    rendered = render(tpl)
    eq_(rendered, 'Hello &lt;p&gt;')


def test_trans_tag():
    """Trans block with tags should not be escaped."""
    s = '{% trans %}this is a <b>test</b>{% endtrans %}'
    eq_(render(s), 'this is a <b>test</b>')


def test_trans_interpolation():
    """Trans block with interpolation should be escaped."""
    s = """
        {% trans what="<a>" %}
        this is a <b>{{ what }}</b>
        {% endtrans %}
        """.strip()
    eq_(render(s), 'this is a <b>&lt;a&gt;</b>')
