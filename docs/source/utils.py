import os

from django.conf import settings, global_settings


def fix_django_settings():
    """Configure Django settings if they are not pre-configured or if we
    haven't been provided settings to use by environment variable.

    Based in
    github.com/django-debug-toolbar/django-debug-toolbar/runtests.py

    """
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
            ],
            MIDDLEWARE_CLASSES=global_settings.MIDDLEWARE_CLASSES + (
                'debug_toolbar.middleware.DebugToolbarMiddleware',
            ),
            ROOT_URLCONF='',
            DEBUG=False,
            SITE_ID=1,
        )
