import json

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Reorder fixtures so some objects come before others.'
    args = '[fixture model ...]'

    def handle(self, fixture, *models, **options):
        output = []
        bucket = {}
        others = []

        for model in models:
            bucket[model] = []

        data = json.loads(file(fixture).read())

        for object in data:
            if object['model'] in bucket.keys():
                bucket[object['model']].append(object)
            else:
                others.append(object)

        for model in models:
            output.extend(bucket[model])

        output.extend(others)
        print json.dumps(output, indent=4)
