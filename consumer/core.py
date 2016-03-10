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


def is_empty(dct):
    '''
    return True if dct values are ALL blank. False, otherwise.
    '''
    resp = True
    for value in dct.values():
        if value:
            resp = False
            break
    return resp


class Rows(object):
    def __init__(self, logger, source):
        self.logger = logger
        self.source = source  # ONE or TWO

    def fetch_rows(self):
        try:
            json_key = json.load(open(config.OAUTH_CONFIG))
            scope = [config.SPREADSHEET[self.source]['SCOPE']]
            credentials = SignedJwtAssertionCredentials(
                    json_key['client_email'],
                    json_key['private_key'].encode(),
                    scope)
            gc = gspread.authorize(credentials)

            sheet = gc.open_by_key(config.SPREADSHEET[self.source]['ID'])
            worksheet = sheet.worksheet(config.SPREADSHEET[self.source]['WORKSHEET'])
        except Exception, err:
            self.logger.error("Cannot open spreadsheet: %s" % str(err))
            raise err

        fields = worksheet.row_values(1)  # headers
        maxid_from_file = json.load(open(config.CONSUMER[self.source]['MAX_ID_FILE']))
        _maxid = int(maxid_from_file['max_id']) - 10 # minus 10 just in case..
        # ..we missed something
        if _maxid < 2:
            _maxid = 2
        
        self.logger.debug('Got worksheet | Starting from row %s' % str(_maxid))

        empty_count = 0
        iteration_counter = 1
        while True:
            ########################################
            # This while loop will keep going      #
            # until it either hits the iteration   #
            # limit (currently set at 50) or       #
            # encounters 5 contiguous blank rows   #
            # on the sheet                         #
            ########################################

            # guard against infinite loops
            if iteration_counter > config.CONSUMER[self.source]['ITERATION_COUNT_LIMIT']:
                self.logger.debug("BREAK")
                break
            iteration_counter += 1


            # fetch row values for `_maxid`
            new_row = worksheet.row_values(int(_maxid))
            self.logger.debug('Consumed row %s::  %s' % (
                str(_maxid), new_row))

            # package row values in dict with headers as keys
            idx = 0
            params = {}
            for item in new_row:
                if not fields[idx] == '':
                    params[fields[idx]] = new_row[idx]
                idx += 1
            
            # send values to web service if row isn't blank.
            # if it's blank, check the next 5 rows. if still blank, break.
            empty = is_empty(params)
            if not empty:
                params['rownumber'] = int(_maxid)
                self.send(params)
                
                # TERMINAL POINT 1
                # write new maxID value to file; then increment
                _file = file(config.CONSUMER[self.source]['MAX_ID_FILE'], 'w')
                json.dump({'max_id': str(_maxid)}, _file)
                _file.close()
                _maxid += 1

                self.logger.debug('Row %s:: Sent to web service' % str(int(_maxid)-1))

                continue
            else:
                limit = config.CONSUMER[self.source]['ITERATION_EMPTY_COUNT']
                # TERMINAL POINT 2(a $ b)
                # write new maxID value to file; then increment
                _file = file(config.CONSUMER[self.source]['MAX_ID_FILE'], 'w')

                self.logger.debug('Row %s empty' % str(int(_maxid)-1))
                if empty_count <= limit:
                    empty_count += 1
                    
                    # 2a
                    json.dump({'max_id': str(_maxid)}, _file)
                    _file.close()
                    _maxid += 1


                    continue
                else:
                    # 2b
                    json.dump({
                        'max_id': str(int(_maxid) - (limit-1))}, _file)
                    _file.close()
                    _maxid += 1

                    self.logger.info("Encountered %s empty rows. Stopped" % str(limit))
                    break



    def send(self, params):
        ws = config.WEB_SERVICE['HOST'] + ':' + str(config.WEB_SERVICE['PORT'])
        url = ws + '/process?'
        args = urlencode(params)
        resp = requests.post(url + args)
