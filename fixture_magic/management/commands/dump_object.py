from __future__ import print_function

from past.builtins import long

import django
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
            'use in a fixture.')
    args = "<[--kitchensink | -k] [--natural] [--query] object_class id [id ...]>"

    def create_parser(self, prog_name, subcommand):
        """Handle parser creation in regards to the Django version."""
        parser = super(Command, self).create_parser(prog_name, subcommand)

        old_django_version = django.VERSION[:2] < (1, 10)
        if old_django_version:
            # Older Django versions (<1.10) handle optparse backwards
            # compatibility in regards to accepting positional args,
            # see:
            # https://github.com/django/django/blob/stable/1.9.x/
            #   django/core/management/base.py#L309
            #
            # We remove the 'args' action here which would otherwise
            # consume too many arguments due to its nargs='*' setting.
            # Django 1.10+ does no longer have that issue.
            args_action = [action for action in parser._actions
                           if action.dest == "args"][0]
            parser._remove_action(args_action)

        return parser

    def add_arguments(self, parser):
        """Add command line arguments to parser"""

        # Required Args
        parser.add_argument(dest='model',
                            help=('Name of the model, with app name first. Eg "app_name.model_name"'))
        parser.add_argument(dest='ids', default=None, nargs='*',
                            help=('Use a list of ids e.g. 0 1 2 3'))

        # Optional args
        parser.add_argument('--kitchensink', '-k',
                            action='store_true', dest='kitchensink',
                            default=False,
                            help='Attempts to get related objects as well.')
        parser.add_argument('--natural', '-n',
                            action='store_true', dest='natural',
                            default=False,
                            help='Use natural keys if they are available.')
        parser.add_argument('--query',
                            dest='query', default=None,
                            help=('Use a json query rather than list of ids '
                                  'e.g. \'{\"pk__in\": [id, ...]}\''))

    def handle(self, *args, **options):
        error_text = ('%s\nTry calling dump_object with --help argument or ' +
                      'use the following arguments:\n %s' % self.args)
        try:
            #verify input is valid
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
