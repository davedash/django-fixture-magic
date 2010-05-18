import json

from django.db import models

serialize_me = []
seen = {}

def reorder_json(data, models):
    output = []
    bucket = {}
    others = []

    for model in models:
        bucket[model] = []

    for object in data:
        if object['model'] in bucket.keys():
            bucket[object['model']].append(object)
        else:
            others.append(object)

    for model in models:
        output.extend(bucket[model])

    output.extend(others)
    return output


def get_fields(obj):
    try:
        return obj._meta.fields
    except AttributeError:
        return []


def serialize_fully():
    index = 0

    while index < len(serialize_me):
        for field in get_fields(serialize_me[index]):
            if isinstance(field, models.ForeignKey):
                add_to_serialize_list(
                    [serialize_me[index].__getattribute__(field.name)])

        index = index + 1

    serialize_me.reverse()


def add_to_serialize_list(objs):
    for obj in objs:
        if obj is None:
            continue

        # Proxy models don't serialize well in Django.
        if obj._meta.proxy:
            obj = obj._meta.proxy_for_model.objects.get(pk=obj.pk)

        key = "%s:%s:%s" % (obj._meta.app_label, obj._meta.module_name,
                            obj.pk)
        if key not in seen:
            serialize_me.append(obj)
            seen[key] = 1
