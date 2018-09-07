import unittest
import redis
import json
import logging
from gspread import gspread
from stacomms import config
from stacomms.consumer import core
from oauth2client.client import SignedJwtAssertionCredentials
from stacomms.consumer import server_stacomms_daemon as consumer1
from stacomms.consumer import server_stacomms_daemon_2 as consumer2

class ConsumerTests(unittest.TestCase):

    def setUp(self, ):
        pass

    def tearDown(self, ):
        pass

    def test_is_empty(self, ):
        resp = dict()
        resp[1] = core.is_empty(dict())
        resp[2] = core.is_empty(dict(foo='', bar=''))
        resp[3] = core.is_empty(dict(foo=1, bar=2))
        resp[4] = core.is_empty(dict(foo='one', bar='two'))
        resp[5] = core.is_empty(dict(foo='one', bar=''))
        for each in resp.keys():
            self.assertIsInstance(resp[each], bool, msg="return type not boolean")
        self.assertTrue(resp[1], "incorrect output")
        self.assertTrue(resp[2], "incorrect output")
        self.assertFalse(resp[3], "incorrect output")
        self.assertFalse(resp[4], "incorrect output")
        self.assertFalse(resp[5], "incorrect output")

    def test_setup(self, ):
        resp1 = consumer1.setup()
        resp2 = consumer2.setup()
        self.assertIsInstance(resp1, dict, "return type not dict")
        self.assertIsInstance(resp2, dict, "return type not dict")
        self.assertTrue('logger' in resp1, "logger object missing")
        self.assertTrue('logger' in resp2, "logger object missing")
        self.assertIsInstance(resp1['logger'], logging.Logger, msg="incorrect logger type")
        self.assertIsInstance(resp2['logger'], logging.Logger, msg="incorrect logger type")

    def test_redis(self, ):
        logger = logging.Logger('test.log', 'DEBUG')
        source = 'test_suite'
        testkey = 'test.test_redis.test_key'
        testvalue = 'test.test_redis.test_value'
        r = core.Rows(logger, source)
        self.assertIsInstance(r.db['connection'], redis.StrictRedis, msg="Redis connection failure")
        saved = r.db['connection'].set(testkey, testvalue)
        self.assertEqual(saved, 1, msg="redis set failure")
        val = r.db['connection'].get(testkey)
        self.assertEqual(val, testvalue)


    def test_can_open_spreadsheet(self, ):
        '''
        tests that all spreadsheets can be opened, and read
        '''
        for source in config.SPREADSHEET.keys():
            json_key = json.load(open(config.OAUTH_CONFIG))
            scope = [config.SPREADSHEET[source]['SCOPE']]
            credentials = SignedJwtAssertionCredentials(
                    json_key['client_email'],
                    json_key['private_key'].encode(),
                    scope)
            gc = gspread.authorize(credentials)
            sheet = gc.open_by_key(config.SPREADSHEET[source]['ID'])
            worksheet = sheet.worksheet(config.SPREADSHEET[source]['WORKSHEET'])
            self.assertIsInstance(worksheet, gspread.models.Worksheet)
            fields = worksheet.row_values(1)
            self.assertIsInstance(fields, list, msg="row values not in list")

    def test_email(self, ):
        self.assertIn('stacomms.site/me', str(config.EMAIL['TEMPLATE']),
                msg="No link to individual responses page")

    

if __name__ == '__main__':
    unittest.main()
