from django.db import models
from collections import OrderedDict

serialize_me = []
seen = {}


def reorder_json(data, models, ordering_cond=None):
    """Reorders JSON (actually a list of model dicts).

    This is useful if you need fixtures for one model to be loaded before
    another.

    :param data: the input JSON to sort
    :param models: the desired order for each model type
    :param ordering_cond: a key to sort within a model
    :return: the ordered JSON
    """
    if ordering_cond is None:
        ordering_cond = {}
    output = []
    bucket = OrderedDict([])
    others = []
    for model in models:
        bucket.update({model: []})

    for object_d in data:
        if object_d['model'] in bucket.keys():
            bucket[object_d['model']].append(object_d)
        else:
            others.append(object_d)

    for bk in bucket:
        bucket[bk].sort(key=ordering_cond[bk])
        output.extend(bucket[bk])

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

        index += 1

    serialize_me.reverse()


def add_to_serialize_list(objs):
    for obj in objs:
        if obj is None:
            continue
        if not hasattr(obj, '_meta'):
            add_to_serialize_list(obj)
            continue

        # Proxy models don't serialize well in Django.
        if obj._meta.proxy:
            obj = obj._meta.proxy_for_model.objects.get(pk=obj.pk)
        model_name = getattr(obj._meta, 'model_name',
                             getattr(obj._meta, 'module_name', None))
        key = "%s:%s:%s" % (obj._meta.app_label, model_name, obj.pk)

        if key not in seen:
            serialize_me.append(obj)
            seen[key] = 1
