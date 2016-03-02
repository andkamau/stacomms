"""
"""
import json
import uuid
import gspread
import requests
from stacomms import config
from urllib import urlencode
from stacomms.common import log
from oauth2client.client import SignedJwtAssertionCredentials

MAX_ID = json.load(open(config.CONSUMER['MAX_ID_FILE']))

class Rows(object):
    def __init__(self, logger):
        self.logger = logger

    def fetch_rows(self):
        json_key = json.load(open(config.OAUTH_CONFIG))
        scope = [config.SPREADSHEET.get('SCOPE')]
        credentials = SignedJwtAssertionCredentials(
                json_key['client_email'],
                json_key['private_key'].encode(),
                scope)
        gc = gspread.authorize(credentials)

        sheet = gc.open(config.SPREADSHEET.get('TITLE'))
        worksheet = sheet.worksheet(config.SPREADSHEET.get('WORKSHEET'))
        
        fields = worksheet.row_values(1)
        rowcount = int(worksheet.row_count)
        _maxid = int(MAX_ID['max_id'])
        log("Row count: %s || Last row consumed: %s" % (
            str(rowcount), MAX_ID['max_id']), "debug", self.logger)

        if rowcount > _maxid+1:
            for each in range(_maxid+1, rowcount):
                new_row = worksheet.row_values(int(each))
                
                params = {}
                idx = 0
                for item in new_row:
                    if not fields[idx] == '':
                        params[fields[idx]] = new_row[idx]
                    idx += 1
                self.send(params)

                _file = file(config.CONSUMER['MAX_ID_FILE'], 'w')
                json.dump({'max_id': str(each)}, _file)
                _file.close()

                log("Processed row: %s - %s" % (str(each), params),
                        'debug', self.logger)

        else:
            log("No new rows since last run", "debug", self.logger)

    def send(self, params):
        ws = config.WEB_SERVICE['HOST'] + ':' + str(config.WEB_SERVICE['PORT'])
        url = ws + '/process?'
        args = urlencode(params)
        resp = requests.post(url + args)
        self.logger.debug('Sent to API')
