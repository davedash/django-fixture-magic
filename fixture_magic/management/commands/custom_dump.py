from __future__ import print_function

import sys

try:
    import json
except ImportError:
    from django.utils import simplejson as json

from django.core.management.base import BaseCommand
try:
    from django.db.models import loading
except ImportError:
    from django.apps import apps as loading
from django.core.serializers import serialize
from django.conf import settings
from django.template import Variable, VariableDoesNotExist

from fixture_magic.utils import (
    add_to_serialize_list,
    reorder_json,
    serialize_me,
    serialize_fully
)


class Command(BaseCommand):
    help = 'Dump multiple pre-defined sets of objects into a JSON fixture.'

    def add_arguments(self, parser):
        parser.add_argument('dump_name')
        parser.add_argument('pk', nargs='+')
        parser.add_argument('--natural', default=False, action='store_true', dest='natural',
                            help='Use natural keys if they are available.')

    def handle(self, *args, **options):
        # Get the primary object
        dump_name = options['dump_name']
        pks = options['pk']
        dump_settings = settings.CUSTOM_DUMPS[dump_name]
        (app_label, model_name) = dump_settings['primary'].split('.')
        include_primary = dump_settings.get("include_primary", False)
        dump_me = loading.get_model(app_label, model_name)
        objs = dump_me.objects.filter(pk__in=[int(i) for i in pks])
        for obj in objs.all():
            # get the dependent objects and add to serialize list
            for dep in dump_settings['dependents']:
                try:
                    thing = Variable("thing.%s" % dep).resolve({'thing': obj})
                    if hasattr(thing, 'all'):  # Related managers can't be iterated over
                        thing = thing.all()
                    add_to_serialize_list([thing])
                except VariableDoesNotExist:
                    sys.stderr.write('%s not found' % dep)

            if include_primary or not dump_settings['dependents']:
                add_to_serialize_list([obj])

        serialize_fully()
        data = serialize('json', [o for o in serialize_me if o is not None],
                         indent=4,
                         use_natural_foreign_keys=options.get('natural', False),
                         use_natural_primary_keys=options.get('natural', False),
                         )

        data = reorder_json(
            json.loads(data),
            dump_settings.get('order', []),
            ordering_cond=dump_settings.get('order_cond', {})
        )

        print(json.dumps(data, indent=4))
