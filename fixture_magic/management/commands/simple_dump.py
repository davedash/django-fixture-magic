from __future__ import print_function

from optparse import make_option


from django.core.management.base import BaseCommand, CommandError

try:
    from django.db.models import loading
except ImportError:
    from django.apps import apps as loading

from django.core import serializers

from fixture_magic.utils import (add_to_serialize_list, serialize_me, seen, reorder_json,
                                 serialize_fully)


class Command(BaseCommand):
    help = ('Dump specific objects from the database into JSON that you can '
            'use in a fixture.')
    args = "<[--kitchensink | -k] [--natural] [--query] object_class id [id ...]>"

    FIELDS_WRONG = [
        "pk", "id", "required_flat_options",
        "default_consumption_option", "attachments",
        "required_plans", "compatible_plans",
        "conflicting_plans", "required_consumption_options", "compatible_consumption_options",
        "conflicting_consumption_options", "compatible_flat_options", "conflicting_flat_options"
    ]

    def add_arguments(self, parser):
        """Add command line arguments to parser"""

        # Required Args
        parser.add_argument(dest='model',
                            help=(
                                'Name of the model, with app name first. Eg "app_name.model_name"'))

    def handle(self, *args, **options):
        try:
            (app_label, model_name) = options['model'].split('.')
        except AttributeError:
            raise CommandError("Specify model as `appname.modelname")

        dump_me = loading.get_model(app_label, model_name)
        fields = (f for f in dump_me._meta.get_fields()
                  if f.name not in self.FIELDS_WRONG)

        all_fields = [rel.name for rel in fields]
        objs = dump_me.objects.all()
        to_serialize = []
        for obj in objs:
            obj.pk = None
            to_serialize.append(obj)
        data = serializers.serialize('json', to_serialize, fields=all_fields)
        print(data)
