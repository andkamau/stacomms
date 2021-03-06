from twisted.web import http
from twisted.internet import threads
from stacomms.web import core
from stacomms.web.user_responses import User


def log(msg, level):
    print "[%s] %s" % (level.upper(), msg)


def get_params(request):
    '''
    retrieve request params and add to dict
    '''
    try:
        params = {}
        for key, val in request.args.items():
            params[key] = val[0]
        return params
    except Exception, err:
        log('get_params() fail - %r' % err, 'error')
        raise err


def write_response(request):
    '''
    write http response
    '''
    try:
        #request.write(str(response))

        default_resp = "Well Received. Thanks"
        request.write(default_resp)
        request.finish()
    except Exception, err:
        log('write_response() fail - %r' % err, 'error')
        write_error(request, 'error')


def write_error(request, error):
    '''
    write error on http response
    '''
    try:
        #request.write(str(error))

        default_resp = "Error: %s" % str(error)
        request.write(default_resp)
        request.finish()
    except Exception, err:
        log('write_error() fail - %r' % err, 'error')
        return


def setup(func):
    '''
    decorator that extracts http parameters
    from requests object and adds them to `params` dict
    '''
    def __inner(request):
        try:
            params = core.clean_up(get_params(request))
            func(params, request)
        except Exception, err:
            error = 'setup() fail - %r' % err
            log(error, 'error')
            raise err
    return __inner

@setup
def process_request(params, request):
    '''
    Expected params:
    ================
    {'To:': 'Admin',
    'rownumber': '2',
    'Category': 'Change of phone number',
    "Leader's category": 'AL',
    'Timestamp': '2/21/2016 20:07:45',
    "Leader's name": 'Jermaine Cole',
    'Comments': "Kindly change Kendrick's phone number to 32323232",
    'id': 'c6565155-c725-487f-bfba-410e928c195e',
    "Leader's email address": 'jcole@gmail.com',
    "Does the class member have children in Children's Programme?": '',
    "Class member's first name": 'Kendrick',
    'Response': 'Done',
    "Class member's last name": 'Lamar',
    "source": 'ONE'}
    '''
    try:
        if not params:
            print "No URL args. Request dropped"
        else:
            issue = core.Issue(params)
            print "Incoming row %s: %s" % (params['rownumber'], params)
            if not issue.get_issue_from_db():
                issue.save_issue_to_db()

            if issue.has_response() and not issue.notification_sent():
                ## first, update flag to avoid multiple notifications.
                issue.update_issue_in_db('notification_sent', 'True')
                issue.update_response_list()
                ## then send actual notifications
                issue.send_email_notification()
                if issue.requires_sms():
                    issue.send_sms()
            else:
                print "ROW %s: No response |or| Notification sent" % (
                        params['rownumber'])
        
        write_response(request)


    except Exception, err:
        log('process_request() fail - %r -- %s' % (err, params), 'error')
        write_error(request, 'error')

@setup
def process_user_responses(params, request):
    '''
    '''
    try:
        print params
        if 'userid' in params:
            user_id = params['userid']
            args = User(user_id).get_user_history()
            print "User history: %s" % args

            #resp = UserResponse(args)
            #resp.render_GET()
            request.finish()
        else:
            print "ERROR: No userID in request parameters"
            request.finish()

    except Exception, err:
        log('process_user_responses() fail - %r -- %s' % (err, params), 'error')
        write_error(request, 'error')


def get_pages():
    '''
    returns mapping of endpoint : process function
    '''
    return {'/process': process_request,
            '/me': process_user_responses
            }


def catch_error(*args):
    for arg in args:
        log('error from deffered - %r' % arg, 'error')
    return 'system error'


class requestHandler(http.Request):

    pages = get_pages()

    def __init__(self, channel, queued):
        http.Request.__init__(self, channel, queued)

    def process(self):
        if self.path in self.pages:
            handler = self.pages[self.path]
            d = threads.deferToThread(handler, self)
            d.addErrback(catch_error)
            return d
        else:
            self.setResponseCode(http.NOT_FOUND)
            self.write('404 - page not found')
            self.finish()

class requestProtocol(http.HTTPChannel):
    requestFactory = requestHandler

class RequestFactory(http.HTTPFactory):
    protocol = requestProtocol
    isLeaf = True

    def __init__(self):
        http.HTTPFactory.__init__(self)

