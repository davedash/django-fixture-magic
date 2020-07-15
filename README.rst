.. image:: https://travis-ci.org/davedash/django-fixture-magic.svg?branch=master
    :target: https://travis-ci.org/davedash/django-fixture-magic



============
Requirements
============

This package requires:

* Python 2.7, 3.6
* Django 1.8 - 2.1


Installation
------------

You can get fixture-magic from pypi with::

    pip install django-fixture-magic

The development version can be installed with::

    pip install -e git://github.com/davedash/django-fixture-magic#egg=fixture-magic

For use in python3 install the following::

    pip install future

fixture-magic adds two commands to ``manage.py`` therefore you should add it to
your ``INSTALLED_APPS`` in ``settings.py``:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'fixture_magic',
        ...
    )

Usage
-----

There are four commands.  ``dump_object`` returns the json representation of
a specific object as well as all its dependencies (as defined by ForeignKeys)::

    ./manage.py dump_object APP.MODEL PK1 PK2 PK3 ... > my_new_fixture.json

Or:

::

    ./manage.py dump_object APP.MODEL --query '{"pk__in": [PK1, PK2, PK3]}' > my_new_fixture.json

Or you can get all objects with all dependencies by passing an asterisk::

    ./manage.py dump_object APP.MODEL '*' > my_new_fixture.json

You can now safely load ``my_new_fixture.json`` in a test without foreign key i
errors.

By default, fixture magic will dump related fixtures to your model in your fixture.
This can be disabled by passing the option ``--no-follow`` to ``dump_object``. This
is useful if your target database is already partially setup. Here is and example default output of dump_object::

    ./manage.py dump_object APP.Book

.. code-block:: json

    [
      {
          "model": "APP.Author",
          "fields": {
              "pk": 5,
              "name": "Mark Twain",
          }
      },
      {
          "model": "APP.Book",
          "fields": {
              "pk": 2,
              "title": "Tom Sawyer",
              "author": 5
          }
      }
    ]

Running with the ``--no-follow`` options yields:

    ./manage.py dump_object APP.Book --no-follow

.. code-block:: json

    [
      {
          "model": "APP.Book",
          "fields": {
              "pk": 2,
              "title": "Tom Sawyer",
              "author": 5
          }
      }
    ]


:Note: The above example assumes that an Author with an ID of 5 exists in the target database.

The second command is ``merge_fixtures``.  This command takes several fixture
files and does a simple de-dupe operation (based on model and pk) and returns a
clean json file.  This is helpful if you have multiple json fixtures that might
have redundant data::

    ./manage.py merge_fixtures fixture1.json fixture2.json fixture3.json ... \
    > all_my_fixtures.json

The third command is ``reorder_fixtures``.  This command takes a single file
and several model names (in ``app.model`` format as they are specified in
fixture files).  This reorders your fixtures so the models you specifiy first
show up in the fixture first.  This is helpful if you tend to get foreign-key
errors when loading models::

    ./manage.py reorder_fixtures fixture.json APP1.MODEL1 APP2.MODEL2 ... \
    > ordered_fixture.json

Unspecified models will be appended to the end.

The fourth command is ``custom_dump``.  This reads a setting ``CUSTOM_DUMPS``:

.. code-block:: python

    ## Fixture Magic
    CUSTOM_DUMPS = {
        'addon': {  # Initiate dump with: ./manage.py custom_dump addon id
            'primary': 'addons.addon',  # This is our reference model.
            'dependents': [  # These are the attributes/methods of the model that we wish to dump.
                'current_version',
                'current_version.files.all.0',
            ],
            'order': ('app1.model1', 'app2.model2',),
            'order_cond': {'app1.model1': lambda x: 1 if x.get('fields').get('parent_model1') else 0,
                            'app2.model2': lambda x: -1 * x.get('pk')},
        }
    }

It runs the equivalent of ``dump_object`` on the dependents (which in turn pick
up the primary object).  The JSON dumps are then merged together.  Very handy
for dumping multi-dependent objects. `dependents`, `order` and `order_cond` are
optional.

``dependents``: Defines additional properties/methods to dump the return values
of. Magic will convert `"current_version.files.all.0"`
to `object.current_version.files.all()[0]`

``order``: Specify an order in which objects should be dumped based on their
model class. In the above example, all app1.model1 objects will preceed any
app2.model2 objects, which will preceed any objects of any other model class.

``order_cond``: Specify an order to dump objects of one or more particular model
classes. In the above example, all app1.model1 objects with a truthy
`self.parent_model1` attribute will come after any other app1.model1 object that
does not have a truthy value for this attribute. A sort operation is called on
the list of all objects of that model type, with the value associated with a
model name being passed to the sort function as the `key` keyword argument.
Keep in mind that the model objects will have already been serialized to a
dictionary object prior to the sort operation.
