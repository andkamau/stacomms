from stacomms import config
from stacomms.web.core import run_query
import json
import gspread
from stacomms.common import log
from oauth2client.client import SignedJwtAssertionCredentials


class User(object):

    def __init__(self, user_id):
        self.user_id = user_id

    def _get_user_email_address(self):
        """
        get user email from db
        """
        query = config.DB['SELECT_EMAIL'] % self.user_id
        db_resp = run_query(query, db=config.DB['SCHEMA'], port=config.DB['PORT'])
        if db_resp['ok'] and int(db_resp['rows']) > 0:
            email_add = db_resp['message'][0][0]
            return email_add
        else:
            print "ERROR: Cannot get email add for %s" % self.user_id
            return


    def _get_worksheet(self):
        """
        """
        try:
            # open spreadsheet ONE
            json_key = json.load(open(config.OAUTH_CONFIG))
            scope = [config.SPREADSHEET['ONE']['SCOPE']]
            credentials = SignedJwtAssertionCredentials(
                    json_key['client_email'],
                    json_key['private_key'].encode(),
                    scope)
            gc = gspread.authorize(credentials)

            sheet = gc.open_by_key(config.SPREADSHEET['ONE']['ID'])
            worksheet = sheet.worksheet(config.SPREADSHEET['ONE']['WORKSHEET'])
            return worksheet
        except Exception, err:
            print "ERROR: Cannot open spreadsheet: %s" % str(err)
            raise err

    def get_user_history(self):
        """
        """
        email_add = self._get_user_email_address()
        worksheet = self._get_worksheet()
        try:
            fields = worksheet.row_values(1)  # headers
            user_responses = worksheet.findall(email_add)
            print '%s appears in %s cells: %s' % (email_add, len(user_responses), user_responses)
            idx = 0
            user_history = {}
            for cell in user_responses:
                if not fields[idx] == '':
                    row_values = worksheet.row_values(cell.row)
                    user_history[cell.row] = dict(
                            leadersname=row_values[3],
                            timestamp=row_values[0],
                            classmembersname=row_values[5],
                            comments=row_values[8],
                            responses=row_values[11]
                            )

            return user_history
        except Exception, err:
            print "ERROR: get_user_history() fail - %s -- %s" % (err, self.user_id)
            return []


