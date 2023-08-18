case = '''
        {
            "key": "__KEY",
            "value": "__VALUE"
        }
'''

header = '''
        [
            {
                "key": "Api-Key",
                "value": "__API_KEY",
                "type": "default"
            }
        ]
'''

query = ''',
        "query": [__QUERY_DATA]
'''

url = '''
    {
        "raw": "__RAW_URL",
        "protocol": "http",
        "host": [__HOST],
        "port": "__PORT",
        "path": [__PATH]__QUERY
    }
'''

body = ''',
    "body": {
        "mode": "raw",
        "raw": "__BODY_RAW",
        "options": {
            "raw": {
                "language": "json"
            }
        }
    }
'''

item = '''
        {
            "name": "__NAME",
            "request": {
                "method": "__METHOD",
                "header": __HEADER,
                "url": __URL__BODY
            },
            "response": []
        }
        '''

info = '''
{
    "info": {
        "_postman_id": "445902e2-4358-4330-9514-e660daa2025c",
        "name": "__NAME | Auto Generate TestCase by QuyLV",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [__ITEM]
}
'''