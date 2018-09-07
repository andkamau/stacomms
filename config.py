import os
HOME = os.getenv('APPS_HOME') + '/stacomms'

from stacomms.web.html_templates import email_template as EMAIL_TEMPLATE

SERVICE_ID = 'STACOMMS'
SERVICE_NAME = 'St. A'


SPREADSHEET = dict(
        ONE=dict(
        ID=os.getenv("SHEETS_ID"),
        NAME=os.getenv("SHEETS_NAME"),
        TITLE=os.getenv("SHEETS_TITLE"),
        SCOPE='https://spreadsheets.google.com/feeds',
        WORKSHEET=os.getenv("SHEETS_WORKSHEET"),
        FORM=os.getenv("SHEETS_FORM"),
        SMS_KEY='sendsmsnotificationwhenthetlresponds',
        SHARE_EMAIL=os.getenv("SHEETS_SHARE_EMAIL")
        # share the Google spreadsheet with `SHARE_EMAIL`
        ),

        TWO=dict(
            ID='',
            NAME='',
            TITLE='',
            SCOPE='https://spreadsheets.google.com/feeds',
            WORKSHEET='',
            FORM='',
            SMS_KEY='sendsmsnotificationwhentheadminresponds',
            SHARE_EMAIL=''
            # share the Google spreadsheet with `SHARE_EMAIL`
            )
        )
        

OAUTH_CONFIG=''

WEB_SERVICE = dict(
        HOST='http://localhost',
        PORT=6090,
        THREADS=200,
        LOGS='%s/web/logs/' % HOME
        )

RESPONSE_SERVER = dict(
        PORT=6091,
        HOST='https://localhost',
        NAME=''
        )

CONSUMER = dict(
        ONE=dict(
        SLEEP_TIME=3600,
        PID='consumer_one.pid',
        LOGS='log-stacomms-daemon',
        _HOME='%s/consumer' % HOME,
        ITERATION_EMPTY_COUNT=5, # stop row iteration after x empty rows
        ITERATION_COUNT_LIMIT=50 # maximum iterations per loop
        ),

        TWO=dict(
            SLEEP_TIME=3600,
            PID='consumer_two.pid',
            LOGS='log-stacomms-2-daemon',
            _HOME='%s/consumer' % HOME,
            ITERATION_EMPTY_COUNT=5, # stop row iteration after x empty rows
            ITERATION_COUNT_LIMIT=50 # maximum iterations per loop
            )
        )


EMAIL = dict(
        URL='',
        WHITELIST={'toggle': False, #send email only to whitelist addresses
            'list': []
            },
        TEMPLATE=EMAIL_TEMPLATE,
        NOTIFICATIONS=True  # Email notifications toggle
        )


SMS = dict(
        at_username=os.getenv("AT_USERNAME"),
        at_api_key=os.getenv("AT_API_KEY"),
        WHITELIST={
            'toggle': False,
            'list': []
            }
        )


DB = dict(
        SELECT_PHONE="SELECT PHONE_NUMBER FROM USERS WHERE EMAIL_ADDRESS = '%s'",
        SELECT_EMAIL="SELECT EMAIL_ADDRESS FROM USERS WHERE ID = '%s'",
        SELECT_USERID="SELECT ID FROM USERS WHERE EMAIL_ADDRESS = '%s'",
        SCHEMA='STACOMMS',
        PORT=3306
        )

STORAGE = dict(
        REDIS_CONFIG=dict(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            db=0,
            password=os.getenv('REDIS_PASSWORD')
            )
        )
