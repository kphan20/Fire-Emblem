from pymongo import MongoClient
from pprint import pprint
import urllib
# TO DO
# Need to create generic methods to upload files to the database
# Move scraper json files to the database

PASSWORD = urllib.parse.quote('neeg@573P')
DATABASE = 'testing123' # whatever man
client = MongoClient(f"mongodb+srv://testing:{PASSWORD}@maps.elfsp.mongodb.net/{DATABASE}?retryWrites=true&w=majority")
db = client.Test
serverStatusResult = db.command('serverStatus')
pprint(dict((database, [collection for collection in client[database].list_collection_names()]) for database in client.database_names()))


#db.test_document1.insert_one({'testing': True})