"""
"""
import string
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

    def save(self,):
        print "Saving row {rownumber}".format(**self.params)
        return self.cache.memc_client.add(self.params['rownumber'], self.params)

    def get(self,):
        return self.cache.get(self.params['rownumber'])

    def update(self, flag, value):
        self.params[str(flag)] = value
        print "Updating row %s. Adding %s with value %s" % (
                self.params['rownumber'],
                flag, value)
        self.cache.memc_client.replace(self.params['rownumber'], self.params)

    def has_response(self,):
        return True if self.params.get('response') else False

    def notification_sent(self,):
        saved_issue = self.get()
        return True if saved_issue.get('notification_sent') else False

    
    def send_email_notification(self,):
        print "%s | Send email to %s | %s | %s" % (
                self.id,
                self.params["leadersemailaddress"],
                self.params["comments"],
                self.params['response']
                )

    def send_sms_notification(self):
        pass
