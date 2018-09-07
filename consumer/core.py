"""
"""
import json
import uuid
import redis
import requests
from gspread import gspread
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
        self.db = dict(
                connection=redis.StrictRedis(**config.STORAGE['REDIS_CONFIG']),
                maxid_key='%s.%s.maxid'%(config.SERVICE_ID, source),
                responses_key='%s.%s.responded'%(config.SERVICE_ID, source),
                
                )

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

        # fetch the latest row ID fetched
        _maxid = self.db['connection'].get(self.db['maxid_key'])
        if not _maxid:
            _maxid = 2 # take it from the top
        else:
            _maxid = int(_maxid)

        # fetch list of row IDs with responses
        resp_list_raw = self.db['connection'].get(self.db['responses_key'])
        if resp_list_raw:
            resp_list = resp_list_raw.split(',')
        else:
            resp_list = []

        ##
        # Coupl'a things to do now:
        #   a. Find diff between all entries and entries with a response
        #       >>> diff = int(_maxid) - len(resp_list)
        #   b. Find the row IDs without a response:  `no_resp_list`
        #   c. Loop through `no_resp_list`. send responses if updates.
        #   d. Loop through rows starting from `_maxid` till 5 blank rows.
        ##


        diff_count = int(_maxid) - len(resp_list)
        no_resp_list = []
        for row in range(2, int(_maxid)+1):
            if str(row) not in resp_list:
                no_resp_list.append(row)
        
        self.logger.debug('Got worksheet | Starting point: maxid: %s and %s pending responses | Current no_resp_list: %s | Resp_list: %s' % (str(_maxid), len(no_resp_list), no_resp_list, resp_list))

        ## Start of operation for rows with pending responses
        for eachrow in no_resp_list:
            eachrow_details = worksheet.row_values(int(eachrow))
            self.logger.debug('%s - row consumed - %s' % (
                eachrow, eachrow_details))
            # package row values in dict `params` with headers as keys
            idx = 0
            params = {}
            for item in eachrow_details:
                if not fields[idx] == '':
                    params[fields[idx]] = eachrow_details[idx].encode('utf-8').strip()
                idx += 1
            params['rownumber'] = int(eachrow)
            params['source'] = self.source
            self.logger.debug('%s - packaged row values' % eachrow)
            self.send(params)
        ## End of operation for rows with pending responses

        self.logger.debug("=======================================")
        self.logger.debug("Done checking old rows for responses!")
        self.logger.debug("Now looking for new rows...")
        self.logger.debug("=======================================")

        empty_count = 1 
        iteration_counter = 1
        while True:
            ########################################
            # This while loop will keep going      #
            # until it either hits the iteration   #
            # limit (currently set at 50) or       #
            # encounters 5 contiguous blank rows   #
            # on the sheet                         #
            ########################################
            try:
                # guard against infinite loops
                if iteration_counter > config.CONSUMER[self.source]['ITERATION_COUNT_LIMIT']:
                    self.logger.debug(
                            """BREAK - too many rows.
                            The limit is currently seet at %s.
                            You can adjust this on application config""" % (
                                config.CONSUMER[self.source]['ITERATION_COUNT_LIMIT']
                                ))
                    break
                iteration_counter += 1

                # fetch row values for `_maxid`
                new_row = worksheet.row_values(int(_maxid))
                self.logger.debug('%s - row consumed_ - %s' % (
                    str(_maxid), new_row))

                # package row values in dict with headers as keys
                idx = 0
                params = {}
                for item in new_row:
                    if not fields[idx] == '':
                        params[fields[idx]] = new_row[idx].encode('utf-8').strip()
                    idx += 1
                
                # send values to web service if row isn't blank.
                # if it's blank, check the next 5 rows. if still blank, break.
                empty = is_empty(params)
                if not empty:
                    params['rownumber'] = int(_maxid)
                    params['source'] = self.source
                    self.send(params)
                    
                    # TERMINAL POINT 1
                    _maxid += 1

                    self.logger.debug('Row %s:: Sent to web service' % str(int(_maxid)-1))

                    continue
                else:
                    limit = config.CONSUMER[self.source]['ITERATION_EMPTY_COUNT']
                    # TERMINAL POINT 2
                    # increment empty_count
                    self.logger.debug('Row %s empty' % _maxid)
                    if empty_count < limit:
                        empty_count += 1
                        _maxid += 1 # increment this value so it fetches next row on next loop
                        continue
                    else:
                        _maxid = _maxid - int(config.CONSUMER[self.source]['ITERATION_EMPTY_COUNT'])
                        # explanation of above line:
                        # on termination of this while loop, we persist the value
                        # of `_maxid` to enable us know where to begin on the next
                        # run of the daemon.
                        # after n blank rows, we need to set the value to `_maxid`-n
                        # to account for the blank rows.
                        self.logger.info("Encountered %s empty rows. Stopped. Reset _maxid to %s" % (str(limit), _maxid))
                        break

            except Exception, err:
                self.logger.error(
                        "ROW %s - Something failed on this row - %s" % (_maxid, str(err))
                        )
                _maxid += 1
                continue

        # save the last value of _maxid to db
        key = self.db['maxid_key']
        self.db['connection'].set(key, _maxid)


    def send(self, params):
        """
        send request to web service via http
        """
        ws = config.WEB_SERVICE['HOST'] + ':' + str(config.WEB_SERVICE['PORT'])
        url = ws + '/process?'
        args = urlencode(params)
        resp = requests.post(url + args)
