#!/usr/bin/env python

import os
import sys

if __name__ == "__main__":
    # Set up the environment for our test project.
    ROOT = os.path.abspath(os.path.dirname(__file__))

    os.environ['DJANGO_SETTINGS_MODULE'] = 'tower-project.settings'
    sys.path.insert(0, os.path.join(ROOT, 'examples'))

    from django.core.management import execute_from_command_line

    # Run the equivalent of "django-admin.py test"
    sys.argv.insert(1, 'test')

    execute_from_command_line(sys.argv)
