start-consumers:
	python consumer/server_stacomms_daemon.py start && python consumer/server_stacomms_daemon_2.py start

stop-consumers:
	python consumer/server_stacomms_daemon.py stop && python consumer/server_stacomms_daemon_2.py stop

start-webservice:
	twistd -y web/site-stacomms.py

stop-webservice:
	kill -9 `cat twistd.pid`

test:
	python tests/test_consumer_core.py
