import unittest

from pymledger.utils import last_day_of_month


class UtilsTestCase(unittest.TestCase):
    def test_last_day_of_month_2022_02(self):
        self.assertEqual(28, last_day_of_month(2022, 2))  # add assertion here
    def test_last_day_of_month_2022_01(self):
        self.assertEqual(31, last_day_of_month(2022, 1))  # add assertion here
    def test_last_day_of_month_2021_12(self):
        self.assertEqual(31, last_day_of_month(2021, 12))  # add assertion here
    def test_last_day_of_month_2021_11(self):
        self.assertEqual(30, last_day_of_month(2021, 11))  # add assertion here


if __name__ == '__main__':
    unittest.main()
