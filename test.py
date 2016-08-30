import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import config
from pprint import pprint
import uuid

json_key = json.load(open(config.OAUTH_CONFIG))
scope = [config.SPREADSHEET["ONE"].get('SCOPE')]

credentials = SignedJwtAssertionCredentials(json_key['client_email'],
        json_key['private_key'].encode(), scope)
gc = gspread.authorize(credentials)

sheet = gc.open(config.SPREADSHEET["ONE"].get('TITLE'))
wksht = sheet.worksheet(config.SPREADSHEET["ONE"].get('WORKSHEET'))

categories = wksht.row_values(1)
values = wksht.row_values(2)
entry = {}
idx = 0

for value in values:
    if not categories[idx] == '':
        entry[categories[idx]] = values[idx]
    idx += 1

entry['id'] = str(uuid.uuid4())
pprint(entry)
