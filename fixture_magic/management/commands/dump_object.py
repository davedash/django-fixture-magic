from optparse import make_option

from django.core.exceptions import FieldError
from django.core.management.base import BaseCommand
from django.db.models import loading
from django.core.serializers import serialize
from django.db import models


def get_fields(obj):
    try:
        return obj._meta.fields
    except AttributeError:
        return []


serialize_me = []
seen = {}

def add_to_serialize_list(objs):
    for obj in objs:
        if obj is None:
            continue

        # Proxy models don't serialize well in Django.
        if obj._meta.proxy:
            obj = obj._meta.proxy_for_model.objects.get(pk=obj.pk)

        key = "%s:%s:%s" % (obj._meta.app_label, obj._meta.module_name,
                            obj.pk)
        if key not in seen:
            serialize_me.append(obj)
            seen[key] = 1


class Command(BaseCommand):
    help = ('Dump specific objects from the database into JSON that you can '
            'use in a fixture')
    args = "[object_class id ...]"

    option_list = BaseCommand.option_list + (
            make_option('--kitchensink', action='store', dest='kitchensink',
                default=False,
                help='Attempts to get related objects as well.'),
            )

    def handle(self, object_class, *ids, **options):
        (app_label, model_name) = object_class.split('.')
        dump_me = loading.get_model(app_label, model_name)
        objs = dump_me.objects.filter(pk__in=[int(i) for i in ids])

        if options.get('kitchensink'):
            related_fields = [rel.get_accessor_name() for rel in
                          dump_me._meta.get_all_related_objects()]

            for obj in objs:
                for rel in related_fields:
                    try:
                        add_to_serialize_list(obj.__getattribute__(rel).all())
                    except FieldError:
                        pass

        add_to_serialize_list(objs)
        index = 0

        while index < len(serialize_me):
            for field in get_fields(serialize_me[index]):
                if isinstance(field, models.ForeignKey):
                    add_to_serialize_list(
                        [serialize_me[index].__getattribute__(field.name)])

            index = index + 1

        serialize_me.reverse()
        print serialize('json', [o for o in serialize_me if o is not None],
                        indent=4)
