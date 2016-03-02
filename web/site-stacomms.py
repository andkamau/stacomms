#!/usr/bin/python2.7
from twisted.application import internet, service
from stacomms.web.server import RequestFactory
from stacomms.config import WEB_SERVICE
from twisted.python.log import ILogObserver, FileLogObserver
from twisted.python.logfile import DailyLogFile
from twisted.internet import reactor

log = 'twistd-stacomms.log'
ProfilerService = internet.TCPServer(WEB_SERVICE['PORT'], RequestFactory())
ProfilerService.setName('stacomms-http')
application = service.Application('stacomms-http')
ProfilerService.setServiceParent(application)
logfile = DailyLogFile('%s' % log, WEB_SERVICE['LOGS'])
application.setComponent(ILogObserver, FileLogObserver(logfile).emit)
reactor.suggestThreadPoolSize(WEB_SERVICE['THREADS'])
