from __future__ import print_function

from optparse import make_option

from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers import serialize
try:
    from django.db.models import loading
except ImportError:
    from django.apps import apps as loading
import json

from fixture_magic.utils import (add_to_serialize_list, serialize_me, seen,
                                 serialize_fully)


class Command(BaseCommand):
    help = ('Dump specific objects from the database into JSON that you can '
            'use in a fixture')
    args = "<[--kitchensink | -k] object_class id [id ...]>"

    option_list = getattr(BaseCommand, 'option_list', ()) + (
            make_option('--kitchensink', '-k',
                action='store_true', dest='kitchensink',
                default=False,
                help='Attempts to get related objects as well.'),
            make_option('--natural', '-n',
                action='store_true', dest='natural',
                default=False,
                help='Use natural keys if they are available.'),
            make_option('--query',
                dest='query', default=None,
                help=('Use a json query rather than list of ids '
                      'e.g. \'{\"pk__in\": [id, ...]}\'')),
            )


    def handle(self, *args, **options):
        error_text = ('%s\nTry calling dump_object with --help argument or ' +
                      'use the following arguments:\n %s' %self.args)
        try:
            #verify input is valid
            (app_label, model_name) = args[0].split('.')
            query = options['query']
            ids = args[1:]
            if ids and query:
                raise CommandError(error_text % 'either use query or id list, not both')
            if not (ids or query):
                raise CommandError(error_text % 'must pass list of ids or a json --query')
        except IndexError:
            raise CommandError(error_text %'No object_class or filter clause supplied.')
        except ValueError:
            raise CommandError(error_text %("object_class must be provided in"
                    " the following format: app_name.model_name"))
        except AssertionError:
            raise CommandError(error_text %'No filter argument supplied.')

        dump_me = loading.get_model(app_label, model_name)
        if query:
            objs = dump_me.objects.filter(**json.loads(query))
        else:
            if ids[0] == '*':
                objs = dump_me.objects.all()
            else:
                for parser in int, long, str:
                    try:
                        objs = dump_me.objects.filter(pk__in=map(parser, ids))
                    except ValueError:
                        pass
                    else:
                        break

        if options.get('kitchensink'):
            related_fields = [rel.get_accessor_name() for rel in
                          dump_me._meta.get_all_related_objects()]

            for obj in objs:
                for rel in related_fields:
                    try:
                        if hasattr(getattr(obj, rel), 'all'):
                            add_to_serialize_list(getattr(obj, rel).all())
                        else:
                            add_to_serialize_list([getattr(obj, rel)])
                    except FieldError:
                        pass
                    except ObjectDoesNotExist:
                        pass

        add_to_serialize_list(objs)
        serialize_fully()
        self.stdout.write(serialize('json', [o for o in serialize_me if o is not None],
                                    indent=4,
                                    use_natural_foreign_keys=options.get('natural', False),
                                    use_natural_primary_keys=options.get('natural', False)))

        # Clear the list. Useful for when calling multiple dump_object commands with a single execution of django
        del serialize_me[:]
        seen.clear()
