============
Requirements
============

This package requires:

    * Python 2.6
    * Django


Installation
------------

You can get fixture-magic from pypi with: ::

    pip install django-fixture-magic

The development version can be installed with: ::

    pip install -e git://github.com/davedash/django-fixture-magic#egg=django_fixture_magic

fixture-magic adds two commands to ``manage.py`` therefore you should add it to
your ``INSTALLED_APPS`` in ``settings.py``: ::

    INSTALLED_APPS = (
        ...
        'fixture_magic',
        ...
    )

Usage
-----

There are two commands.  ``dump_object`` returns the json representation of
a specific object as well as all its dependencies (as defined by ForeignKeys).

    ./manage.py dump_object APP.MODEL PK1 PK2 PK3 ... > my_new_fixture.json

You can now safely load ``my_new_fixture.json`` in a test without foreign key i
errors.

The second command is ``merge_fixtures``.  This command takes several fixture
files and does a simple de-dupe operation (based on model and pk) and returns a
clean json file.  This is helpful if you have multiple json fixtures that might
have redundant data.

    ./manage.py merge_fixtures fixture1.json fixture2.json fixture3.json ... \
    > all_my_fixtures.json
