from django.conf import settings
from django.db import models
from django.utils.module_loading import import_string

FIXTURE_MAGIC_HANDLERS_SETTING_STRING = 'FIXTURE_MAGIC_HANDLERS'


def prepare_handlers():
    handlers = getattr(
        settings,
        FIXTURE_MAGIC_HANDLERS_SETTING_STRING,
        {},
    )
    for key, handler in handlers.items():
        if isinstance(handler, str):
            handlers[key] = import_string(handler)()
    return handlers


class BaseModelHandler:
    @staticmethod
    def handle(instance):
        """Handle model instance serialization.

        By default it adds all ForeignKey and m2m fields to serialization
        queue.
        """
        from fixture_magic.utils import (
            add_to_serialize_list,
            get_fields,
            get_m2m,
        )
        for field in get_fields(instance):
            if isinstance(field, models.ForeignKey):
                add_to_serialize_list(
                    [getattr(instance, field.name)],
                )
        for field in get_m2m(instance):
            add_to_serialize_list(
                getattr(instance, field.name).all(),
            )
