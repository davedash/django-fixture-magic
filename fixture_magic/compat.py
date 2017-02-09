

def get_all_related_objects(model):
    try:
        return model._meta.get_all_related_objects()
    except AttributeError:
        return [
            f for f in model._meta.get_fields() if
            (f.one_to_many or f.one_to_one) and
            f.auto_created and not f.concrete
        ]
