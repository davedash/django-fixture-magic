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

There are four commands.  ``dump_object`` returns the json representation of
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

The third command is ``reorder_fixtures``.  This command takes a single file
and several model names (in ``app.model`` format as they are specified in
fixture files).  This reorders your fixtures so the models you specifiy first
show up in the fixture first.  This is helpful if you tend to get foreign-key
errors when loading models.

    ./manage.py reorder_fixtures fixture.json APP1.MODEL1 APP2.MODEL2 ... \
    > ordered_fixture.json

Unspecified models will be appended to the end.

The fourth command is ``custom_dump``.  This reads a setting ``CUSTOM_DUMPS``:

::

    ## Fixture Magic
    CUSTOM_DUMPS = {
        'addon': {  # ./manage.py custom_dump addon id
            'primary': 'addons.addon',  # This is our reference model.
            'dependents': [  # These are items we wish to dump.
                'current_version',
                # Magic turns this into current_version.files.all()[0].
                'current_version.files.all.0',
            ],
            'order': ('app1.model1', 'app2.model2',)  # stuff gets sorted
        }
    }

It runs the equivalent of ``dump_object`` on the dependents (which in turn pick
up the primary object).  The JSON dumps are then merged together.  Very handy
for dumping multi-dependent objects.
