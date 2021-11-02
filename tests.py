import unittest
import time
from crawler import get_txns_parallel, get_txns_serial


class Test_Get_Txns(unittest.TestCase):
    def setUp(cls):
        cls.startTime = time.time()

    def tearDown(cls):
        _time = time.time() - cls.startTime
        print(f"Time taken -> {_time:.4f} seconds")

    def test_get_txns_parallel_requests(self):
        res = None
        try:
            res = get_txns_parallel(using="requests")
        except Exception as e:
            print(e)
                        
        print("\nsample -> ", res[0])
        self.assertIsNotNone(res)

    def test_get_txns_serial_requests(self):
        res = None
        try:
            res = get_txns_serial(using="requests")
        except Exception as e:
            print(e)
                        
        print("\nsample -> ", res[0])
        self.assertIsNotNone(res)

    def test_get_txns_parallel_requests_html(self):
        res = None
        try:
            res = get_txns_parallel(using="requests_html")
        except Exception as e:
            print(e)
                        
        print("\nsample -> ", res[0])
        self.assertIsNotNone(res)

    def test_get_txns_serial_requests_html(self):
        res = None
        try:
            res = get_txns_serial(using="requests_html")
        except Exception as e:
            print(e)
                        
        print("\nsample -> ", res[0])
        self.assertIsNotNone(res)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(Test_Get_Txns)
    unittest.TextTestRunner(verbosity=0).run(suite)