from optparse import make_option

from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers import serialize
from django.db.models import loading

from fixture_magic.utils import (add_to_serialize_list, serialize_me,
        serialize_fully)


class Command(BaseCommand):
    help = ('Dump specific objects from the database into JSON that you can '
            'use in a fixture')
    args = "<[--kitchensink | -k] object_class id1 [id2 [...]]>"

    option_list = BaseCommand.option_list + (
            make_option('--kitchensink', '-k',
                action='store_true', dest='kitchensink',
                default=False,
                help='Attempts to get related objects as well.'),
            )

    def handle(self, *args, **options):
        error_text = ('%s\nTry caling dump_object with --help argument or use'+
                ' the following arguments:\n %s' %self.args)
        try:
            #verify input is valid
            (app_label, model_name) = args[0].split('.')
            ids = args[1:]
            assert(ids)
        except IndexError:
            raise CommandError(error_text %'No object_class or id arguments supplied.')
        except ValueError:
            raise CommandError(error_text %("object_class must be provided in"+
                    " the following format: app_name.model_name"))
        except AssertionError:
            raise CommandError(error_text %'No id arguments supplied.')

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
