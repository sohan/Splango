#!/usr/bin/env python
"""Got this from django-debug-toolbar. The only changes were:

* replace 'debug_toolbar' with 'splango' in INSTALLED_APPS
* replace 'debug_toolbar.middleware.DebugToolbarMiddleware' with
  'splango.middleware.ExperimentsMiddleware' in MIDDLEWARE_CLASSES
* PEP8-fy a little

Source: django-debug-toolbar/runtests.py @ 18bd5da161

"""
import sys
import os
from os.path import dirname, abspath
from optparse import OptionParser

from django.conf import settings, global_settings

# For convenience configure settings if they are not pre-configured or if we
# haven't been provided settings to use by environment variable.
if not settings.configured and not os.environ.get('DJANGO_SETTINGS_MODULE'):
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.admin',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',

            'splango',

            'tests',
        ],
        MIDDLEWARE_CLASSES=global_settings.MIDDLEWARE_CLASSES + (
            'splango.middleware.ExperimentsMiddleware',
        ),
        ROOT_URLCONF='',
        DEBUG=False,
        SITE_ID=1,
    )

from django.test.simple import DjangoTestSuiteRunner


def runtests(*test_args, **kwargs):
    if 'south' in settings.INSTALLED_APPS:
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()

    if not test_args:
        test_args = ['tests']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    test_runner = DjangoTestSuiteRunner(
        verbosity=kwargs.get('verbosity', 1),
        interactive=kwargs.get('interactive', False),
        failfast=kwargs.get('failfast'))
    failures = test_runner.run_tests(test_args)
    sys.exit(failures)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
        '--failfast', action='store_true', default=False, dest='failfast')

    (options, args) = parser.parse_args()

    runtests(failfast=options.failfast, *args)
