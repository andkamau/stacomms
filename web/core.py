"""
"""
from stacomms import config

class Issue(object):
    def __init__(self, params):
        self.params = params
        self.id = params.get('id')
    
    def send_email_notification(self,):
        return "%s | Send email to %s | %s" % (
                self.id,
                self.params["Leader's email address"],
                self.params["Comments"]
                )

    def send_sms_notification(self):
        pass
