from __future__ import print_function

from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers import serialize

from fixture_magic.compat import get_all_related_objects

try:
    from django.db.models import loading
except ImportError:
    from django.apps import apps as loading
import json

from fixture_magic.utils import (add_to_serialize_list, serialize_me, seen,
                                 serialize_fully)


class Command(BaseCommand):
    help = ('Dump specific objects from the database into JSON that you can '
            'use in a fixture.')
    args = "<[--kitchensink | -k] [--natural]  [--natural-primary]  '\
    '[--natural-foreign] [--query] object_class id [id ...]>"

    def add_arguments(self, parser):
        """Add command line arguments to parser"""

        # Required Args
        parser.add_argument(dest='model',
                            help='Name of the model, with app name first.'
                            ' Eg "app_name.model_name"')
        parser.add_argument(dest='ids', default=None, nargs='*',
                            help='Use a list of ids e.g. 0 1 2 3')

        # Optional args
        parser.add_argument('--kitchensink', '-k',
                            action='store_true', dest='kitchensink',
                            default=False,
                            help='Attempts to get related objects as well.')
        parser.add_argument('--natural', '-n',
                            action='store_true', dest='natural',
                            default=False,
                            help='Use natural foreign and primary keys '
                            'if they are available.')
        parser.add_argument('--natural-primary',
                            action='store_true', dest='natural_primary',
                            default=False,
                            help='Use natural primary keys if they are available.')
        parser.add_argument('--natural-foreign',
                            action='store_true', dest='natural_foreign',
                            default=False,
                            help='Use natural foreign keys if they are available.')
        parser.add_argument('--query',
                            dest='query', default=None,
                            help=('Use a json query rather than list of ids '
                                  'e.g. \'{\"pk__in\": [id, ...]}\''))
        parser.add_argument('--no-follow',
                            action='store_false', dest='follow_fk',
                            default=True,
                            help='does not serialize Foriegn Keys related to object')

        parser.add_argument(
            '--format', default='json', dest='format',
            help='Specifies the output serialization format for fixtures.',
        )

    def handle(self, *args, **options):
        error_text = ('%s\nTry calling dump_object with --help argument or ' +
                      'use the following arguments:\n %s' % self.args)
        try:
            # verify input is valid
            try:
                (app_label, model_name) = options['model'].split('.')
            except AttributeError:
                raise CommandError("Specify model as `appname.modelname")
            query = options['query']
            ids = options['ids']
            if ids and query:
                raise CommandError(error_text % 'either use query or id list, not both')
            if not (ids or query):
                raise CommandError(error_text % 'must pass list of --ids or a json --query')
        except IndexError:
            raise CommandError(error_text % 'No object_class or filter clause supplied.')
        except ValueError:
            raise CommandError(
                error_text %
                "object_class must be provided in the following format: app_name.model_name"
            )
        except AssertionError:
            raise CommandError(error_text % 'No filter argument supplied.')

        dump_me = loading.get_model(app_label, model_name)
        if query:
            objs = dump_me.objects.filter(**json.loads(query))
        else:
            if ids[0] == '*':
                objs = dump_me.objects.all()
            else:
                try:
                    parsers = int, long, str
                except NameError:
                    parsers = int, str
                for parser in parsers:
                    try:
                        objs = dump_me.objects.filter(pk__in=map(parser, ids))
                    except ValueError:
                        pass
                    else:
                        break

        if options.get('kitchensink'):
            fields = get_all_related_objects(dump_me)

            related_fields = [rel.get_accessor_name() for rel in fields]

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

        if options.get('follow_fk', True):
            serialize_fully()
        else:
            # reverse list to match output of serializez_fully
            serialize_me.reverse()

        natural_foreign = (options.get('natural', False) or
                           options.get('natural_foreign', False))
        natural_primary = (options.get('natural', False) or
                           options.get('natural_primary', False))

        self.stdout.write(serialize(options.get('format', 'json'),
                                    [o for o in serialize_me if o is not None],
                                    indent=4,
                                    use_natural_foreign_keys=natural_foreign,
                                    use_natural_primary_keys=natural_primary))

        # Clear the list. Useful for when calling multiple
        # dump_object commands with a single execution of django
        del serialize_me[:]
        seen.clear()
