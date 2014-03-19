import os

TEST_RUNNER = 'django_nose.runner.NoseTestSuiteRunner'

ROOT = os.path.dirname(os.path.abspath(__file__))
path = lambda *a: os.path.join(ROOT, *a)

DATABASES = {
    'default': {
        'NAME': 'test.db',
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = (
    'django_nose',
)

def JINJA_CONFIG():
    import jinja2
    from django.conf import settings
    config = {'extensions': ['tower.template.i18n',
                             'jinja2.ext.with_', 'jinja2.ext.loopcontrols'],
              'finalize': lambda x: x if x is not None else ''}
    return config

DOMAIN_METHODS = { }

TOWER_KEYWORDS = {
    '_lazy': None,
}

SECRET_KEY = 'useless not secret key used for tests'
