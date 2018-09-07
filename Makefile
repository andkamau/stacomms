start-consumer:
	python consumer/server_stacomms_daemon.py start

stop-consumer:
	python consumer/server_stacomms_daemon.py stop

start-webservice:
	twistd -y web/site-stacomms.py

stop-webservice:
	kill -9 `cat twistd.pid`

test:
	python tests/test_consumer_core.py
