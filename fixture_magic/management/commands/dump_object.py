from optparse import make_option

from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db.models import loading
from django.core.serializers import serialize

from fixture_magic.utils import (get_fields, add_to_serialize_list,
                                 serialize_me, seen, serialize_fully)


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
        try:
            objs = dump_me.objects.filter(pk__in=[int(i) for i in ids])
        except ValueError:
            # We might have primary keys thar are just strings...
            objs = dump_me.objects.filter(pk__in=ids)

        if options.get('kitchensink'):
            related_fields = [rel.get_accessor_name() for rel in
                          dump_me._meta.get_all_related_objects()]

            for obj in objs:
                for rel in related_fields:
                    try:
                        add_to_serialize_list(obj.__getattribute__(rel).all())
                    except FieldError:
                        pass
                    except ObjectDoesNotExist:
                        pass

        add_to_serialize_list(objs)
        serialize_fully()
        print serialize('json', [o for o in serialize_me if o is not None],
                        indent=4)
