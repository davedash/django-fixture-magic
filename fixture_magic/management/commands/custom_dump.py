import sys
try:
    import json
except ImportError:
    from django.utils import simplejson as json

from django.core.management.base import BaseCommand
from django.db.models import loading
from django.core.serializers import serialize
from django.conf import settings
from django.template import Variable, VariableDoesNotExist

from fixture_magic.utils import (add_to_serialize_list, reorder_json,
        serialize_me, serialize_fully)


class Command(BaseCommand):
    help = 'Dump multiple pre-defined sets of objects into a JSON fixture.'
    args = "[dump_name pk]"

    def handle(self, dump_name, pk, **options):
        # Get the primary object
        dump_settings = settings.CUSTOM_DUMPS[dump_name]
        (app_label, model_name) = dump_settings['primary'].split('.')
        dump_me = loading.get_model(app_label, model_name)
        obj = dump_me.objects.get(pk=pk)
        # get the dependent objects and add to serialize list
        for dep in dump_settings['dependents']:
            try:
                thing = Variable("thing.%s" % dep).resolve({'thing': obj})
                add_to_serialize_list([thing])
            except VariableDoesNotExist:
                sys.stderr.write('%s not found' % dep)

        if not dump_settings['dependents']:
            add_to_serialize_list([obj])

        serialize_fully()
        data = serialize('json', [o for o in serialize_me if o is not None])

        data = reorder_json(json.loads(data), dump_settings.get('order', []),
                ordering_cond=dump_settings.get('order_cond',{}))

        print json.dumps(data, indent=4)
