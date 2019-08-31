from bson.objectid import ObjectId


def remove_object_ids_from_dict(di):
    for k, v in di.items():
        if isinstance(v, dict):
            remove_object_ids_from_dict(v)
        elif isinstance(v, list):
            remove_object_ids_from_list(v)
        else:
            if isinstance(v, ObjectId):
                di[k] = str(v)
    return di

def remove_object_ids_from_list(li):
    for i, v in enumerate(li):
        if isinstance(v, dict):
            remove_object_ids_from_dict(v)
        elif isinstance(v, list):
            remove_object_ids_from_list(v)
        else:
            if isinstance(v, ObjectId):
                li[i] = str(v)
    return li
