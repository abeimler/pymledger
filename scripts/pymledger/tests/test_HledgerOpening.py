import unittest

from pymledger.HledgerOpening import get_opening


class HledgerOpeningGetOpening(unittest.TestCase):
    def test_get_opening_empty(self):
        expected = """"""
        self.assertEqual(expected, get_opening(2022, 1, {}, status='', cl=False))  # add assertion here

    def test_get_opening_with_entires(self):
        data = [{'account': 'expenses:Test', 'amount': 100.0, 'currency': 'EUR'}]
        expected = """2022-01-01 opening balances  ; opening:
    expenses:Test                                                         100,00 EUR
    equity:opening/closing balances
"""
        self.assertEqual(expected, get_opening(2022, 1, data, status='', cl=False))  # add assertion here

    def test_get_opening_with_entires_budget(self):
        data = [{'account': 'assets:budget:Test', 'amount': 100.0, 'currency': 'EUR', 'budget': True}]
        expected = """2022-01-01 opening balances  ; opening:
    (assets:budget:Test)                                                  100,00 EUR
    equity:opening/closing balances
"""
        self.assertEqual(expected, get_opening(2022, 1, data, status='', cl=False))  # add assertion here

    def test_get_opening_with_entires_with_status(self):
        data = [{'account': 'expenses:Test', 'amount': 100.0, 'currency': 'EUR'}]
        expected = """2022-01-01 * opening balances  ; opening:
    expenses:Test                                                         100,00 EUR
    equity:opening/closing balances
"""
        self.assertEqual(expected, get_opening(2022, 1, data, status='*', cl=False))  # add assertion here

    def test_get_opening_with_entires_with_cl(self):
        data = [{'account': 'expenses:Test', 'amount': 100.0, 'currency': 'EUR'}]
        expected = """2022-01-01 * opening balances  ; clopen:2022, opening:
    expenses:Test                                                         100,00 EUR
    equity:opening/closing balances
"""
        self.assertEqual(expected, get_opening(2022, 1, data, status='*', cl=True))  # add assertion here


if __name__ == '__main__':
    unittest.main()
