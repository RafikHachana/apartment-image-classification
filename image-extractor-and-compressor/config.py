MONGODB_CONNECTION_URL = 'mongodb://localhost:27017/'

DATABASES = {
    'CSV': {
        'MAPPER': 'standards'
    },
    'MONGODB': {
        'name': 'adsDB',
        'connection_url': MONGODB_CONNECTION_URL,
        'collections': [
            'morizon',
            'otodom'
        ]
    },
}
