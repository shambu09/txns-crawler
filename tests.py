import unittest
import time
from crawler import get_txns_parallel, get_txns_serial


class Test_Get_Txns(unittest.TestCase):
    def setUp(cls):
        cls.startTime = time.time()

    def tearDown(cls):
        _time = time.time() - cls.startTime
        print(f"{_time:.4f} seconds", end=" -> ", flush=True)

    def test_get_txns_parallel_requests(self):
        return get_txns_parallel(using="requests")

    def test_get_txns_serial_requests(self):
        return get_txns_serial(using="requests")

    def test_get_txns_parallel_requests_html(self):
        return get_txns_parallel(using="requests_html")

    def test_get_txns_serial_requests_html(self):
        return get_txns_serial(using="requests_html")


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(Test_Get_Txns)
    unittest.TextTestRunner(verbosity=0).run(suite)