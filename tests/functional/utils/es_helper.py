import json


def prepare_for_es_insert(data: list[dict], index: str) -> str:

    bulk_query = []
    for row in data:
        bulk_query.extend([
            json.dumps({'index': {'_index': index, '_id': str(row['id'])}}),
            json.dumps(row)
        ])

    str_query = '\n'.join(bulk_query) + '\n'
    return str_query
