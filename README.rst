=============================
imagery
=============================

Django application to manage the download and processing of Landsat Imagery


Quickstart
----------

Install imagery

::

    pip install git+https://github.com/ibamacsr/imagery.git

Add imagery and some dependencies to your INSTALLED_APPS:

::

    INSTALLED_APPS=[
        ...
        "django.contrib.gis",
        "imagery",
        "rest_framework",
        "rest_framework_gis",
        ...
    ]

Add a it to the URL conf of your project:

::

    url(r'^', include("imagery.urls", namespace="imagery")),

Override imagery/base.html template with the same code contained inside the comment blog.

You can use this template as the base.html of your project: https://gist.github.com/willemarcel/13469c1756b4bdb8136f

Features
--------

* TODO

Running Tests
--------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements-test.txt
    (myenv) $ python runtests.py

Credits
---------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-pypackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
