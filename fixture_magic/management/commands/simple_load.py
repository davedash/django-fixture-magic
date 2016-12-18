from __future__ import print_function

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

try:
    from django.db.models import loading
except ImportError:
    from django.apps import apps as loading

from django.core import serializers

class Command(BaseCommand):
    help = ('Dump specific objects from the database into JSON that you can '
            'use in a fixture.')
    args = "<[--kitchensink | -k] [--natural] [--query] object_class id [id ...]>"


    def add_arguments(self, parser):
        """Add command line arguments to parser"""

        # Required Args
        parser.add_argument('--file', '-f',
                            dest='infile',
                            help=(
                                'Name of the model, with app name first. Eg "app_name.model_name"'))

    def handle(self, *args, **options):
        infile = options['infile']
        objs = []
        with open(infile) as filere:
            objs = list(serializers.deserialize("json", filere))
            for obj in objs:
                print (obj)
                obj.save()
                print("Loading: %s" % obj)
        print("Finish load: %s" % len(objs))
