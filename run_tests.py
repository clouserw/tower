#!/usr/bin/env python

import os
import sys


# Set up the environment for our test project.
ROOT = os.path.abspath(os.path.dirname(__file__))

os.environ['DJANGO_SETTINGS_MODULE'] = 'tower-project.settings'
sys.path.insert(0, os.path.join(ROOT, 'examples'))

# This can't be imported until after we've fiddled with the
# environment.
from django.test.utils import setup_test_environment
setup_test_environment()

from django.core.management import call_command

# Run the equivalent of "django-admin.py test"
try:
    from django import setup
    setup()
except ImportError:
    # Django 1.6 and below does not require setup()
    pass
call_command('test')
