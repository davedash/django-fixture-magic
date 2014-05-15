from django.db import models

serialize_me = []
seen = {}


def reorder_json(data, models, ordering_cond={}):
    """Reorders JSON (actually a list of model dicts).

    This is useful if you need fixtures for one model to be loaded before
    another.

    :param data: the input JSON to sort
    :param models: the desired order for each model type
    :param ordering_cond: a key to sort within a model
    :return: the ordered JSON
    """
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
        if ordering_cond.has_key(model):
            bucket[model].sort(key=ordering_cond[model])
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

        index += 1

    serialize_me.reverse()


def add_to_serialize_list(objs, using):
    for obj in objs:
        if obj is None:
            continue
        if not hasattr(obj, '_meta'):
            add_to_serialize_list(obj, using)
            continue

        # Proxy models don't serialize well in Django.
        if obj._meta.proxy:
            obj = obj._meta.proxy_for_model.objects.using(using).get(pk=obj.pk)

        key = "%s:%s:%s" % (obj._meta.app_label, obj._meta.module_name,
                            obj.pk)
        if key not in seen:
            serialize_me.append(obj)
            seen[key] = 1
