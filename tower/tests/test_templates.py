import jingo
import jinja2
from test_utils import eq_


def render(s, context={}):
    """Render a template string."""
    t = jingo.env.from_string(s)
    return t.render(**context)


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
