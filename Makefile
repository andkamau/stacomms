start-consumer:
	python consumer/server_stacomms_daemon.py

start-webservice:
	twistd -y web/site-stacomms.py

test:
	python tests/test_consumer_core.py
