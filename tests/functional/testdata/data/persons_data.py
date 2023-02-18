import uuid


data_with_freeze_id = [
    {
        'id': '640d1ac4-0f5a-465b-a75c-45945d28198b',
        'name': 'Ann',
        'role': ['Actor'],
        'film_ids': [
            '647d1ac4-0f5a-465b-a75c-45941d28198b'
        ]
    }
]
data = [
    {
        'id': str(uuid.uuid4()),
        'name': 'Bob',
        'role': ['Director'],
        'film_ids': [
            str(uuid.uuid4()),
            str(uuid.uuid4())
        ]
    } for _ in range(60)
]

data.extend(data_with_freeze_id)
