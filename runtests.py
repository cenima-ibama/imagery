import sys

try:
    from django.conf import settings
    from django.test.utils import get_runner


    settings.configure(
        DEBUG=True,
        USE_TZ=True,
        DATABASES={
            'default': {
                 'ENGINE': 'django.contrib.gis.db.backends.postgis',
                 'NAME': 'imagery',
                 'USER': 'postgres',
             }
        },
        ROOT_URLCONF="imagery.urls",
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.sessions",
            "django.contrib.contenttypes",
            "django.contrib.sites",
            "django.contrib.staticfiles",
            "django.contrib.gis",
            "imagery",
            "rest_framework",
            "rest_framework_gis",
        ],
        SITE_ID=1,
        MIDDLEWARE_CLASSES=(
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        ),
        REST_FRAMEWORK={
            'DEFAULT_RENDERER_CLASSES': (
                'rest_framework.renderers.JSONRenderer',
            ),
        },
        MEDIA_ROOT="tests/media/",
    )

    try:
        import django
        setup = django.setup
    except AttributeError:
        pass
    else:
        setup()

except ImportError:
    import traceback
    traceback.print_exc()
    raise ImportError("To fix this error, run: pip install -r requirements-test.txt")


def run_tests(*test_args):
    if not test_args:
        test_args = ['tests']

    # Run tests
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    failures = test_runner.run_tests(test_args)

    if failures:
        sys.exit(bool(failures))


if __name__ == '__main__':
    run_tests(*sys.argv[1:])
