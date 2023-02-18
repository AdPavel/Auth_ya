import uuid


data_with_freeze_id = [
    {
        'id': '640d1ac4-0f5a-465b-a75c-45941d28198b',
        'name': 'Drama',
        'description': ''
    }
]
data = [
    {
        'id': str(uuid.uuid4()),
        'name': 'Documentary',
        'description': ''

    } for _ in range(60)
]

data.extend(data_with_freeze_id)
