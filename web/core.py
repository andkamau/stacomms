"""
"""
import json
import string
import urllib
import redis
import requests
from stacomms import config
from stacomms.web.AfricasTalkingGateway import AfricasTalkingGateway

from db_utilities.mysql.core import run_query


def clean_up(params):
    cleanparams = {}
    try:
        for key in params:
            cleankey = (key.translate(string.maketrans("", ""),
                    string.punctuation)).replace(
                            " ", ""
                            ).lower()
            cleanparams[cleankey] = params.get(key)
        return cleanparams

    except Exception, err:
        print 'ERROR: clean_up() fail - %s' % str(err)
        raise err


class Issue(object):

    def __init__(self, params):
        self.params = params
        self.id = params.get('rownumber')
        self.db_key = '{source}.{rownumber}'.format(**params)
        self.db = redis.StrictRedis(**config.STORAGE['REDIS_CONFIG'])

    
    def get_issue_from_db(self, ):
        return self.db.get(self.db_key)


    def save_issue_to_db(self, ):
        print "Saving row {rownumber} in redis".format(**self.params)
        return self.db.set(self.db_key, self.params, nx=True)


    def update_issue_in_db(self, flag, value):
        self.params[str(flag)] = value
        print "Updating row %s. Adding %s with value %s" % (
                self.params['rownumber'], flag, value)
        return self.db.set(self.db_key, self.params, xx=True)

    
    def update_response_list(self, ):
        '''
        Add the row number to the list of rows with responses
        '''
        responses_key = '%s.%s.responded' %(
                config.SERVICE_ID, self.params['source'])
        length = self.db.append(responses_key,
                ',%s' % self.params['rownumber'])
        print '%s - Updated resp_list. List length now %s' % (
                self.params['rownumber'],
                length)


    def has_response(self,):
        return True if self.params.get('responses') else False


    def notification_sent(self,):
        _issue = self.get_issue_from_db()
        try:
            saved_issue = eval(_issue)
            return True if saved_issue.get('notification_sent') else False
        except Exception, err:
            print "%s - ERR: Cannot eval DB response: %s" % (
                    self.params['rownumber'], _issue)
            return False


    def construct_sms(self,):
        user_id = self.get_user_id()
        if not user_id: 
            return """%s comms response about {classmembersname}:\n TL / Admin said: {responses}.
            """.format(**self.params) % (config.SERVICE_NAME)
        else:
            return """%s comms response about {classmembersname}:\n TL / Admin said: {responses}.\n
            """.format(**self.params) % (config.SERVICE_NAME)



    def requires_sms(self,):
        return True if self.params[(config.SPREADSHEET[self.params['source']]['SMS_KEY'])].startswith('Yes') else False

    def get_phone_number(self,):
        '''
        from DB - using email address

        returns a list of valid mobile numbers for current user
        '''
        try:
            query = config.DB['SELECT_PHONE'] % self.params['leadersemailaddress']
            db_resp = run_query(query, db=config.DB['SCHEMA'], port=config.DB['PORT'])
            if db_resp['ok'] and int(db_resp['rows']) > 0:
                phonenos = db_resp['message'][0][0].split(',') # comma separated list of phone numbers

                valid_mobile_numbers = []
                for phoneno in phonenos:
                    num = phoneno.replace(' ', '').replace('-','')
                    numba = num[:10]
                    if numba.isdigit() and numba.startswith('07'):
                        valid_mobile_numbers.append(
                                '254%s' % numba[1:]
                                )

                print "DEBUG: Phone numbers for %s - %s" % (
                        self.params['leadersemailaddress'],
                        valid_mobile_numbers)
                self.params['phone_numbers'] = valid_mobile_numbers
                return valid_mobile_numbers
            else:
                print "ERR: Unexpected response from DB: %s -- %s" % (
                        db_resp, self.params)
                return []

        except Exception, err:
            print "ERROR: get_phone_number() - %s -- %s" % (
                    str(err), self.params)
            raise err



    def send_sms(self,):
        try:
            phone_numbers = self.get_phone_number() # list of numbers
            message = self.construct_sms()
            for phone_number in phone_numbers:
                if config.SMS['WHITELIST']['toggle'] and phone_number not in config.SMS['WHITELIST']['list']:
                    print "SMS NOT SENT - %s not in whitelist" % phone_number
                else:
                    gateway = AfricasTalkingGateway(
                            config.SMS["at_username"],
                            config.SMS["at_api_key"])
                    msisdn = "+254%s" % str(phone_number).strip()[-9:]
                    resp = gateway.sendMessage(msisdn, message)
                    if not resp[0]["status"] == "Success":
                        print "ERROR: send_sms()- AT resp: %s -- %s" %(
                                resp, self.params)
                    else:
                        print "SMS sent to %s -- %s" % (msisdn, message)
        except Exception, err:
            print "ERROR: send_sms() - %s -- %s" % (err, self.params)
            raise err


    def construct_email(self,):
        return config.EMAIL['TEMPLATE'].format(**self.params) % (
                config.SPREADSHEET[self.params['source']]['NAME']
                )

    def get_user_id(self, ):
        """
        get user ID from db
        """
        query = config.DB['SELECT_USERID'] % self.params['leadersemailaddress']
        db_resp = run_query(query, db=config.DB['SCHEMA'], port=config.DB['PORT'])
        print "Email: %s | UserID: %s" % (self.params['leadersemailaddress'],
                db_resp.get('message'))
        if db_resp['ok'] and int(db_resp['rows']) > 0:
            userid = db_resp['message'][0][0]
            return userid
        else:
            err = "ERROR: Cannot retrieve user ID from DB -- %s" % self.params
            print err
            return
    
    def send_email_notification(self,):
        '''
        send email to the leader's email address
        '''
        self.params['user_id'] = self.get_user_id()
        email = self.construct_email()
        recipient = self.params['leadersemailaddress']
        args = {
                'to': recipient,
                'html': email,
                'to_name': self.params['leadersname'],
                'from_name': '%s Comms' % config.SERVICE_NAME,
                'subject': '%s Communications Response | [%s:%s]' % (config.SERVICE_NAME,
                    self.params['leadersname'], self.params['timestamp'].strip())
                }
        resp = False
        if config.EMAIL['NOTIFICATIONS']:
            if not config.EMAIL['WHITELIST']['toggle']:
                resp = requests.post(config.EMAIL['URL'], data=args)
            else:
                if recipient.lower() in config.EMAIL['WHITELIST']['list']:
                    resp = requests.post(config.EMAIL['URL'], data=args)
        if resp:
            print "Email to %s | %s: %s" % (
                    recipient, str(resp.status_code), resp.text)
        else:
            print "Row %s: EMAIL NOT SENT: Notifications: {NOTIFICATIONS}, WHITELIST: {WHITELIST}".format(**config.EMAIL) % self.params['rownumber']

