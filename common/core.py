"""
common utility functions
"""
from datetime import datetime


EXCEPTIONS = {}
EXCEPTIONS['missingParameter'] = 'Parameter Missing: %s'
EXCEPTIONS['invalid_action'] = 'Invalid Action Invoked: %s'


class MissingParameterException(Exception):
    '''Exception raised when a requisite parameters is missing'''
    def __init__(self, missingParameter):
        error = EXCEPTIONS['missingParameter'] % str(missingParameter)
        self.value = error
    def __str__(self):
        return repr(self.value)


def log(msg, level='debug', logger=None):
    '''
    logs to logger if available, else prints to stdout
    '''
    msg = msg.replace('\n', '\/n')
    if logger:
        eval("logger.%s(msg)" % level)
    else:
        print "%s - %s" % (level.upper(), msg)


def datetime_to_epoch(date):
    '''
    converts an obj of type <type 'datetime.datetime'> to epoch

    :param   date         <type 'datetime.datetime'>
    :return  epoch_date   <type 'int'>
    '''
    return int(date.strftime('%s'))


def verify_params(res, params, logger=None):
    '''checks to verify that all requisite parameters are
    bundled in a dict.

    :params:
        resources dict, 
        params list, 
        logger obj (optional)

    - If logger arg is nog supplied, we will look for logger in res dict.
      If it isn't in res either, then output will be printed on screen
    '''
    if logger:
        logger = {'logger':logger}
    else:
        if res.has_key('logger'):
            logger = {'logger':res['logger']}
        else:
            logger = {}

    try:
        assert isinstance(params, list)
    except AssertionError:
        log(logger, ' utilities.common.core.verifyParams. \
                Cannot evaluate. params is not a list', 'error')
        raise
    for param in params:
        try:
            assert res.has_key(param)
        except AssertionError:
            log(logger, 'operation:verifyParams. FAILED', 'error')
            raise MissingParameterException(param)
    #log(logger, 'All Parameters verified', 'debug')
