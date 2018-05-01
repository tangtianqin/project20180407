import unittest
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

from BarcodeInfoDB import BarcodeInfoDB

class ProductInfoDBTestCase(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()
    
    def tearDown(self):
        self.testbed.deactivate()
    # [END datastore_example_teardown]

    def test2BarcodeInfo(self):
        k = BarcodeInfoDB(Name='test', Barcode='1234567890123').put()
        #print(k.id())
        i = k.get()
        #print(i.Name)
        self.assertEqual(1L, long(k.id()))
        self.assertEqual('test', i.Name)
        dict_info = i.to_dict()
        dict_info['id'] = 1L
        bi = BarcodeInfoDB.from_dict(dict_info)
        self.assertEqual(1L, bi.key.id())
     # [START datastore_example_teardown]
    
# [START main]
if __name__ == '__main__':
    unittest.main()
# [END main]
