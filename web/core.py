"""
"""
import string
from stacomms import config


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
        self.id = params.get('id')

    
    def send_email_notification(self,):
        return "%s | Send email to %s | %s" % (
                self.id,
                self.params["leadersemailaddress"],
                self.params["comments"]
                )

    def send_sms_notification(self):
        pass
