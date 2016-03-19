import uuid
from time import sleep
import logging, os, sys
from stacomms.consumer.daemon import Daemon
from stacomms.consumer.core import Rows
from logging.handlers import TimedRotatingFileHandler
from stacomms.common import log
from stacomms.config import CONSUMER


class PollingDaemon(Daemon):
    
    def run(self):
        loggers = setup()
        logger = loggers['logger']
        logger.info('polling daemon starting ....')
        while True:
            try:
                _id = str(uuid.uuid4())
                logger.debug('starting iteration %s' % _id)
                rows = Rows(logger, 'TWO')
                rows.fetch_rows()
                logger.debug('finished iteration %s' % _id)

            except Exception, err:
                logger.error("Error in daemon - %s" % str(err))

            sleep(CONSUMER['TWO']['SLEEP_TIME'])
            

def setup():
    try:
        loggers = {}
        cwd = CONSUMER['TWO']['_HOME']
        logger = logging.getLogger(CONSUMER['TWO']['LOGS'])
        logger.setLevel(logging.DEBUG)
        ch = TimedRotatingFileHandler('%s/logs/%s.log' % (cwd,
            CONSUMER['TWO']['LOGS']), 'midnight')
        formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        loggers['logger'] = logger

    except Exception, e:
        try:
            logger.error(str(e))
        except:
            pass
        print str(e)
        sys.exit(2)
    else:
        return loggers


if __name__ == '__main__':    
    daemon = PollingDaemon(os.getcwd()+'/'+CONSUMER['TWO']['PID'])
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            print 'daemon stoping ....'
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            print 'daemon restarting ....'
            daemon.restart()
        else:
            print "unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2) 
