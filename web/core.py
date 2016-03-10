"""
"""
import string
import urllib
import requests
from stacomms import config
from stacomms.common.memcache.core import MemcacheHandler


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
        self.cache = MemcacheHandler()
        self.cache_key = '{source}.{rownumber}'.format(**params)

    def save(self,):
        print "Saving row {rownumber}".format(**self.params)
        return self.cache.memc_client.add(self.cache_key, self.params)

    def get(self,):
        return self.cache.get(self.cache_key)

    def update(self, flag, value):
        self.params[str(flag)] = value
        print "Updating row %s. Adding %s with value %s" % (
                self.params['rownumber'],
                flag, value)
        self.cache.memc_client.replace(self.cache_key, self.params)

    def has_response(self,):
        return True if self.params.get('responses') else False

    def notification_sent(self,):
        saved_issue = self.get()
        return True if saved_issue.get('notification_sent') else False

    def construct_email(self,):
        return config.EMAIL['TEMPLATE'].format(**self.params) % (
                config.SPREADSHEET[self.params['source']]['NAME'],
                config.SPREADSHEET[self.params['source']]['FORM'])

    
    def send_email_notification(self,):
        '''
        send email to the leader's email address
        '''
        email = self.construct_email()
        recipient = self.params['leadersemailaddress']
        args = {
                'to': recipient,
                'html': email,
                'to_name': self.params['leadersname'],
                'from_name': 'St.A Comms',
                'subject': 'St. A Communications Response | [%s:%s]' % (
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

    def send_sms_notification(self):
        pass
