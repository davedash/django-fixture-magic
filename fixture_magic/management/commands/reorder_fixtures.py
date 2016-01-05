from __future__ import print_function

try:
    import json
except ImportError:
    from django.utils import simplejson as json

from django.core.management.base import BaseCommand

from fixture_magic.utils import reorder_json


class Command(BaseCommand):
    help = 'Reorder fixtures so some objects come before others.'
    args = '[fixture model ...]'

    def handle(self, fixture, *models, **options):
        output = reorder_json(json.loads(open(fixture).read()), models)

        print(json.dumps(output, indent=4))
