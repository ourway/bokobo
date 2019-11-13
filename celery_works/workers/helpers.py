from ..snippets import logger


def get_object_from_gateway(auth_token, domain, entity, entity_id):
    indexing_gateway_function = domain + '.' + entity

    logger('gateway import',
           {'indexing_gateway_function': indexing_gateway_function})


    # obj = get_by_id(auth_token, entity_id)
    obj = {}
    logger('object from gateway', {'gateway object': obj})

    return obj
