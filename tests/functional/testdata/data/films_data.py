import uuid

data_with_freeze_id = [
        {
            'id': "647d1ac4-0f5a-465b-a75c-45941d28198b",
            'imdb_rating': 1.5,
            'genre': [
                {'id': str(uuid.uuid4()), 'name': 'Action'},
                {'id': str(uuid.uuid4()), 'name': 'Sci-Fi'}
            ],
            'title': 'The Star',
            'description': 'New World',
            'directors_names': ['Stan', 'Quentin'],
            'actors_names': ['Ann', 'Bob'],
            'writers_names': ['Ben', 'Howard'],
            'directors': [
                {'id': str(uuid.uuid4()), 'name': 'Ann'},
                {'id': str(uuid.uuid4()), 'name': 'Bob'}
            ],
            'actors': [
                {'id': str(uuid.uuid4()), 'name': 'Ann'},
                {'id': str(uuid.uuid4()), 'name': 'Bob'}
            ],
            'writers': [
                {'id': str(uuid.uuid4()), 'name': 'Ben'},
                {'id': str(uuid.uuid4()), 'name': 'Howard'}
            ],

        }

]
data = [{
            'id': str(uuid.uuid4()),
            'imdb_rating': 8.5,
            'genre': [
                {'id': str(uuid.uuid4()), 'name': 'Action'},
                {'id': str(uuid.uuid4()), 'name': 'Sci-Fi'}
            ],
            'title': 'The Star',
            'description': 'New World',
            'directors_names': ['Stan', 'Quentin'],
            'actors_names': ['Ann', 'Bob'],
            'writers_names': ['Ben', 'Howard'],
            'directors': [
                {'id': str(uuid.uuid4()), 'name': 'Ann'},
                {'id': str(uuid.uuid4()), 'name': 'Bob'}
            ],
            'actors': [
                {'id': str(uuid.uuid4()), 'name': 'Ann'},
                {'id': str(uuid.uuid4()), 'name': 'Bob'}
            ],
            'writers': [
                {'id': str(uuid.uuid4()), 'name': 'Ben'},
                {'id': str(uuid.uuid4()), 'name': 'Howard'}
            ],

        } for _ in range(60)]

data.extend(data_with_freeze_id)