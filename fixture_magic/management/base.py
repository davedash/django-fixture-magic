from django.core.management.base import BaseCommand


class BaseDumperCommand(BaseCommand):
        try:
            return obj._meta.fields
        except AttributeError:
            return []
