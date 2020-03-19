from __future__ import (
    print_function,
    unicode_literals,
)

from six import string_types

import json

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Merge a series of fixtures and remove duplicates.'

    def add_arguments(self, parser):
        parser.add_argument('args', metavar='files', nargs='+', help='One or more fixture.')

    def handle(self, *files, **options):
        """
        Load a bunch of json files.  Store the pk/model in a seen dictionary.
        Add all the unseen objects into output.
        """
        seen = set()
        output = []

        for file_ in files:
            with open(file_, 'r') as fp:
                data = json.load(fp)
            for obj in data:
                model_name = obj['model']
                if 'pk' in obj.keys():
                    key_unique = obj['pk']
                else:
                    key_unique = '|'.join([
                        value
                        for value in obj['fields'].values()
                        if isinstance(value, string_types)
                    ])
                key = '{}|{}'.format(model_name, key_unique)

                if key not in seen:
                    seen.add(key)
                    output.append(obj)

        print(json.dumps(output, sort_keys=True, indent=4))
