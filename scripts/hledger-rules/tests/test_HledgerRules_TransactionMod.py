import unittest

from pymledger.HledgerRules import gen_transaction_mod


class HledgerRulesGenTransactionModTestCase(unittest.TestCase):
    def test_gen_transaction_mod_empty(self):
        expected = """"""
        self.assertEqual(expected, gen_transaction_mod('',  ''))  # add assertion here

    def test_gen_transaction_mod_with_query_no_account(self):
        expected = """"""
        self.assertEqual(expected, gen_transaction_mod('expenses:Test', ''))  # add assertion here

    def test_gen_transaction_mod(self):
        expected = """= expenses:Test 
    assets:Test                                                                                   *-1

"""
        self.assertEqual(expected, gen_transaction_mod('expenses:Test', 'assets:Test'))  # add assertion here

    def test_gen_transaction_mod_with_space(self):
        expected = """= "expenses:Test Space" 
    assets:Test                                                                                   *-1

"""
        self.assertEqual(expected, gen_transaction_mod('expenses:Test Space', 'assets:Test'))  # add assertion here

    def test_gen_transaction_mod_not_account(self):
        expected = """= expenses:Test not:acct:"assets:Test:Abo" 
    assets:Test                                                                                   *-1

"""
        self.assertEqual(expected, gen_transaction_mod('expenses:Test', 'assets:Test', not_acct='assets:Test:Abo'))  # add assertion here

    def test_gen_transaction_mod_date(self):
        expected = """= expenses:Test date:"2022-02"
    assets:Test                                                                                   *-1

"""
        self.assertEqual(expected, gen_transaction_mod('expenses:Test', 'assets:Test', date='2022-02'))  # add assertion here

    def test_gen_transaction_mod_not_date(self):
        expected = """= expenses:Test not:date:"2022-02"
    assets:Test                                                                                   *-1

"""
        self.assertEqual(expected, gen_transaction_mod('expenses:Test', 'assets:Test', not_date='2022-02'))  # add assertion here

    def test_gen_transaction_mod_not_account_date(self):
        expected = """= expenses:Test not:acct:"assets:Test:Abo" date:"2022-02"
    assets:Test                                                                                   *-1

"""
        self.assertEqual(expected, gen_transaction_mod('expenses:Test', 'assets:Test', not_acct='assets:Test:Abo', date='2022-02'))  # add assertion here

    def test_gen_transaction_mod_not(self):
        expected = """= expenses:Test not:cur:USD 
    assets:Test                                                                                   *-1

"""
        self.assertEqual(expected, gen_transaction_mod('expenses:Test', 'assets:Test', not_query='cur:USD'))  # add assertion here



if __name__ == '__main__':
    unittest.main()
