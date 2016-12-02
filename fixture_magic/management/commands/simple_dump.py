from __future__ import print_function

from optparse import make_option


from django.core.management.base import BaseCommand, CommandError

try:
    from django.db.models import loading
except ImportError:
    from django.apps import apps as loading

import json
import uuid
from django.core import serializers

from fixture_magic.utils import (add_to_serialize_list, serialize_me, seen, reorder_json,
                                 serialize_fully)


class Command(BaseCommand):
    help = ('Dump specific objects from the database into JSON that you can '
            'use in a fixture.')
    args = "<[--kitchensink | -k] [--natural] [--query] object_class id [id ...]>"


    def add_arguments(self, parser):
        """Add command line arguments to parser"""

        # Required Args
        parser.add_argument(dest='model',
                            help=(
                                'Name of the model, with app name first. Eg "app_name.model_name"'))
        parser.add_argument('--file', '-f',
                            dest='outfile',
                            help=(
                                'Name of the model, with app name first. Eg "app_name.model_name"'))

    def handle(self, *args, **options):
        try:
            (app_label, model_name) = options['model'].split('.')
        except AttributeError:
            raise CommandError("Specify model as `appname.modelname")

        outfile = options['outfile']

        dump_me = loading.get_model(app_label, model_name)
        fields = (f for f in dump_me._meta.get_fields()
                  if not f.one_to_many or not f.one_to_one or not f.foreignkey or not f.name == "id")

        all_fields = [rel.name for rel in fields]
        objs = dump_me.objects.all()
        data = serializers.serialize('json', list(objs), fields=all_fields)
        print(data)

        del serialize_me[:]
        seen.clear()
