from __future__ import print_function

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

from fixture_magic.utils import (
    add_to_serialize_list,
    reorder_json,
    serialize_fully
)


def process_dep(parent, dep, serialize_me, seen):
    parts = dep.split('.')
    current = parts.pop(0)
    leftover = '.'.join(parts)

    try:
        thing = getattr(parent, current)
    except AttributeError:
        pass  # related object not found
    else:
        if hasattr(thing, 'all'):
            children = thing.all()
        else:
            children = [thing]
        add_to_serialize_list(children, serialize_me, seen)

        if leftover:
            for child in children:
                process_dep(child, leftover, serialize_me, seen)


class Command(BaseCommand):
    help = 'Dump multiple pre-defined sets of objects into a JSON fixture.'

    def add_arguments(self, parser):
        parser.add_argument('dump_name')
        parser.add_argument('pk', nargs='*')
        parser.add_argument('--natural', default=False, action='store_true', dest='natural',
                            help='Use natural keys if they are available.')

    def handle(self, *args, **options):
        serialize_me = []
        seen = set()
        # Get the primary object
        dump_name = options['dump_name']
        pks = options['pk']
        dump_settings = settings.CUSTOM_DUMPS[dump_name]
        app_label, model_name, *manager_method = dump_settings['primary'].split('.')
        include_primary = dump_settings.get("include_primary", False)

        default_manager = loading.get_model(app_label, model_name).objects
        if manager_method:
            queryset = getattr(default_manager, manager_method[0])()
        else:
            queryset = default_manager.all()
        if pks:
            queryset = queryset.filter(pk__in=pks)

        deps = dump_settings.get('dependents', [])
        for obj in queryset:
            # get the dependent objects and add to serialize list
            for dep in deps:
                process_dep(obj, dep, serialize_me, seen)
            if include_primary or not deps:
                add_to_serialize_list([obj], serialize_me, seen)

        serialize_fully(serialize_me, seen)
        data = serialize(
            'json', [o for o in serialize_me if o is not None],
            indent=4,
            use_natural_foreign_keys=options.get('natural', False),
            use_natural_primary_keys=options.get('natural', False),
        )

        data = reorder_json(
            json.loads(data),
            dump_settings.get('order', []),
            ordering_cond=dump_settings.get('order_cond', {})
        )

        self.stdout.write(json.dumps(data, indent=4))
