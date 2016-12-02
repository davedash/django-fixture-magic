from __future__ import print_function

from optparse import make_option


from django.core.management.base import BaseCommand, CommandError

try:
    from django.db.models import loading
except ImportError:
    from django.apps import apps as loading

import json
import uuid

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
                            dest='infile',
                            help=(
                                'Name of the model, with app name first. Eg "app_name.model_name"'))

    def handle(self, *args, **options):
        try:
            (app_label, model_name) = options['model'].split('.')
        except AttributeError:
            raise CommandError("Specify model as `appname.modelname")

        infile = options['infile']

        dump_me = loading.get_model(app_label, model_name)
        allobjs = json.loads(infile)
        for obj in allobjs:
            dump_me.objects.create(**obj)
            print("Loading: %s" % obj)