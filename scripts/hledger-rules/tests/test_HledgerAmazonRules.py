import unittest

from pymledger.HledgerAmazonRules import gen_amazon_rule


class HledgerAmazonRulesGenAmazonRuleTestCase(unittest.TestCase):
    #maxDiff = None
    def test_gen_amazon_rule_empty(self):
        config = {}
        rule = {}
        expected = """"""
        actual, account = gen_amazon_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual(None, account)  # add assertion here

    def test_gen_amazon_rule_order(self):
        config = {
            'amazon': {
                'if_format': [
                    '{order}.*Amazon.de{ref}AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
                    '{order}.*Amazon .Mktplce{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                    '{order}.*AMZN Mktp DE{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                ],
                'payee': 'AMAZON PAYMENTS EUROPE S.C.A.',
            },
        }
        rule = {
            'order': '111-2222222-3333333',
            'account': 'Expenses:Unterhaltung:Multimedia:Musik:Amazon',
        }
        expected = """
if 111-2222222-3333333.*Amazon.de.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND
111-2222222-3333333.*Amazon .Mktplce.*AMAZON PAYMENTS EUROPE S.C.A.
111-2222222-3333333.*AMZN Mktp DE.*AMAZON PAYMENTS EUROPE S.C.A.
    description AMAZON PAYMENTS EUROPE S.C.A. | Amazon 111-2222222-3333333
    comment type:%buchungstext, payee:AMAZON PAYMENTS EUROPE S.C.A., order:111-2222222-3333333
    account1    Expenses:Unterhaltung:Multimedia:Musik:Amazon                   

"""
        actual, account = gen_amazon_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Unterhaltung:Multimedia:Musik:Amazon', account)  # add assertion here

    def test_gen_amazon_rule_order_disabled(self):
        config = {
            'amazon': {
                'if_format': [
                    '{order}.*Amazon.de{ref}AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
                    '{order}.*Amazon .Mktplce{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                    '{order}.*AMZN Mktp DE{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                ],
                'payee': 'AMAZON PAYMENTS EUROPE S.C.A.',
            },
        }
        rule = {
            'order': '111-2222222-3333333',
            'account': 'Expenses:Unterhaltung:Multimedia:Musik:Amazon',
            'disabled': True,
        }
        expected = """
;if 111-2222222-3333333.*Amazon.de.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND
;111-2222222-3333333.*Amazon .Mktplce.*AMAZON PAYMENTS EUROPE S.C.A.
;111-2222222-3333333.*AMZN Mktp DE.*AMAZON PAYMENTS EUROPE S.C.A.
;    description AMAZON PAYMENTS EUROPE S.C.A. | Amazon 111-2222222-3333333
;    comment type:%buchungstext, payee:AMAZON PAYMENTS EUROPE S.C.A., order:111-2222222-3333333
;    account1    Expenses:Unterhaltung:Multimedia:Musik:Amazon                   

"""
        actual, account = gen_amazon_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual(None, account)  # add assertion here

    def test_gen_amazon_rule_payee(self):
        config = {
            'amazon': {
                'if_format': [
                    '{order}.*Amazon.de{ref}AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
                    '{order}.*Amazon .Mktplce{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                    '{order}.*AMZN Mktp DE{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                ],
                'payee': 'AMAZON PAYMENTS EUROPE S.C.A.',
            },
        }
        rule = {
            'order': '111-2222222-3333333',
            'account': 'Expenses:Unterhaltung:Multimedia:Musik:Amazon',
            'payee': 'AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
        }
        expected = """
if 111-2222222-3333333.*Amazon.de.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND
111-2222222-3333333.*Amazon .Mktplce.*AMAZON PAYMENTS EUROPE S.C.A.
111-2222222-3333333.*AMZN Mktp DE.*AMAZON PAYMENTS EUROPE S.C.A.
    description AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND | Amazon 111-2222222-3333333
    comment type:%buchungstext, payee:AMAZON EU S.A R.L. NIEDERLASSUNG DEUTSCHLAND, order:111-2222222-3333333
    account1    Expenses:Unterhaltung:Multimedia:Musik:Amazon                   

"""
        actual, account = gen_amazon_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Unterhaltung:Multimedia:Musik:Amazon', account)  # add assertion here

    def test_gen_amazon_rule_no_payee(self):
        config = {
            'amazon': {
                'if_format': [
                    '{order}.*Amazon.de{ref}AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
                    '{order}.*Amazon .Mktplce{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                    '{order}.*AMZN Mktp DE{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                ],
            },
        }
        rule = {
            'order': '111-2222222-3333333',
            'account': 'Expenses:Unterhaltung:Multimedia:Musik:Amazon',
        }
        expected = """
if 111-2222222-3333333.*Amazon.de.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND
111-2222222-3333333.*Amazon .Mktplce.*AMAZON PAYMENTS EUROPE S.C.A.
111-2222222-3333333.*AMZN Mktp DE.*AMAZON PAYMENTS EUROPE S.C.A.
    description %payee | Amazon 111-2222222-3333333
    comment type:%buchungstext, payee:%payee, order:111-2222222-3333333
    account1    Expenses:Unterhaltung:Multimedia:Musik:Amazon                   

"""
        actual, account = gen_amazon_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Unterhaltung:Multimedia:Musik:Amazon', account)  # add assertion here

    def test_gen_amazon_rule_description(self):
        config = {
            'amazon': {
                'if_format': [
                    '{order}.*Amazon.de{ref}AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
                    '{order}.*Amazon .Mktplce{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                    '{order}.*AMZN Mktp DE{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                ],
                'payee': 'AMAZON PAYMENTS EUROPE S.C.A.',
            },
        }
        rule = {
            'order': '111-2222222-3333333',
            'account': 'Expenses:Unterhaltung:Multimedia:Musik:Amazon',
            'payee': 'AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
            'description': 'My Fav. Band CD'
        }
        expected = """
if 111-2222222-3333333.*Amazon.de.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND
111-2222222-3333333.*Amazon .Mktplce.*AMAZON PAYMENTS EUROPE S.C.A.
111-2222222-3333333.*AMZN Mktp DE.*AMAZON PAYMENTS EUROPE S.C.A.
    description AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND | Amazon My Fav. Band CD
    comment type:%buchungstext, payee:AMAZON EU S.A R.L. NIEDERLASSUNG DEUTSCHLAND, order:111-2222222-3333333
    account1    Expenses:Unterhaltung:Multimedia:Musik:Amazon                   

"""
        actual, account = gen_amazon_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Unterhaltung:Multimedia:Musik:Amazon', account)  # add assertion here

    def test_gen_amazon_rule_full_description(self):
        config = {
            'amazon': {
                'if_format': [
                    '{order}.*Amazon.de{ref}AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
                    '{order}.*Amazon .Mktplce{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                    '{order}.*AMZN Mktp DE{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                ],
                'payee': 'AMAZON PAYMENTS EUROPE S.C.A.',
            },
        }
        rule = {
            'order': '111-2222222-3333333',
            'account': 'Expenses:Unterhaltung:Multimedia:Musik:Amazon',
            'full_description': 'Amazon Musik | Amazon My Fav. Band CD'
        }
        expected = """
if 111-2222222-3333333.*Amazon.de.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND
111-2222222-3333333.*Amazon .Mktplce.*AMAZON PAYMENTS EUROPE S.C.A.
111-2222222-3333333.*AMZN Mktp DE.*AMAZON PAYMENTS EUROPE S.C.A.
    description Amazon Musik | Amazon My Fav. Band CD
    comment type:%buchungstext, payee:AMAZON PAYMENTS EUROPE S.C.A., order:111-2222222-3333333
    account1    Expenses:Unterhaltung:Multimedia:Musik:Amazon                   

"""
        actual, account = gen_amazon_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Unterhaltung:Multimedia:Musik:Amazon', account)  # add assertion here

    def test_gen_amazon_rule_full_description_payee(self):
        config = {
            'amazon': {
                'if_format': [
                    '{order}.*Amazon.de{ref}AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
                    '{order}.*Amazon .Mktplce{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                    '{order}.*AMZN Mktp DE{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                ],
                'payee': 'AMAZON PAYMENTS EUROPE S.C.A.',
            },
        }
        rule = {
            'order': '111-2222222-3333333',
            'account': 'Expenses:Unterhaltung:Multimedia:Musik:Amazon',
            'payee': 'AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
            'full_description': 'Amazon Musik | Amazon My Fav. Band CD'
        }
        expected = """
if 111-2222222-3333333.*Amazon.de.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND
111-2222222-3333333.*Amazon .Mktplce.*AMAZON PAYMENTS EUROPE S.C.A.
111-2222222-3333333.*AMZN Mktp DE.*AMAZON PAYMENTS EUROPE S.C.A.
    description Amazon Musik | Amazon My Fav. Band CD
    comment type:%buchungstext, payee:AMAZON EU S.A R.L. NIEDERLASSUNG DEUTSCHLAND, order:111-2222222-3333333
    account1    Expenses:Unterhaltung:Multimedia:Musik:Amazon                   

"""
        actual, account = gen_amazon_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Unterhaltung:Multimedia:Musik:Amazon', account)  # add assertion here

    def test_gen_amazon_rule_ref(self):
        config = {
            'amazon': {
                'if_format': [
                    '{order}.*Amazon.de{ref}AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
                    '{order}.*Amazon .Mktplce{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                    '{order}.*AMZN Mktp DE{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                ],
                'payee': 'AMAZON PAYMENTS EUROPE S.C.A.',
            },
        }
        rule = {
            'order': '111-2222222-3333333',
            'account': 'Expenses:Unterhaltung:Multimedia:Musik:Amazon',
            'payee': 'AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
            'ref': 'AAAAABBBBBCCCCCD',
        }
        expected = """
if 111-2222222-3333333.*Amazon.de.*AAAAABBBBBCCCCCD.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND
111-2222222-3333333.*Amazon .Mktplce.*AAAAABBBBBCCCCCD.*AMAZON PAYMENTS EUROPE S.C.A.
111-2222222-3333333.*AMZN Mktp DE.*AAAAABBBBBCCCCCD.*AMAZON PAYMENTS EUROPE S.C.A.
    description AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND | Amazon 111-2222222-3333333
    comment type:%buchungstext, payee:AMAZON EU S.A R.L. NIEDERLASSUNG DEUTSCHLAND, order:111-2222222-3333333, ref:AAAAABBBBBCCCCCD
    account1    Expenses:Unterhaltung:Multimedia:Musik:Amazon                   

"""
        actual, account = gen_amazon_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Unterhaltung:Multimedia:Musik:Amazon', account)  # add assertion here

    def test_gen_amazon_rule_amount(self):
        config = {
            'amazon': {
                'if_format': [
                    '{order}.*Amazon.de{ref}.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
                    '{order}.*Amazon .Mktplce{ref}.*AMAZON PAYMENTS EUROPE S.C.A.',
                    '{order}.*AMZN Mktp DE{ref}.*AMAZON PAYMENTS EUROPE S.C.A.',
                ],
                'payee': 'AMAZON PAYMENTS EUROPE S.C.A.',
            },
        }
        rule = {
            'order': '111-2222222-3333333',
            'account': 'Expenses:Unterhaltung:Multimedia:Musik:Amazon',
            'payee': 'AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
            'ref': 'AAAAABBBBBCCCCCD',
            'amount': 19.99,
        }
        expected = """
if 111-2222222-3333333.*Amazon.de.*AAAAABBBBBCCCCCD.*.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND.*, 19,99
111-2222222-3333333.*Amazon.de.*AAAAABBBBBCCCCCD.*.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND.*,19,99
111-2222222-3333333.*Amazon .Mktplce.*AAAAABBBBBCCCCCD.*.*AMAZON PAYMENTS EUROPE S.C.A..*, 19,99
111-2222222-3333333.*Amazon .Mktplce.*AAAAABBBBBCCCCCD.*.*AMAZON PAYMENTS EUROPE S.C.A..*,19,99
111-2222222-3333333.*AMZN Mktp DE.*AAAAABBBBBCCCCCD.*.*AMAZON PAYMENTS EUROPE S.C.A..*, 19,99
111-2222222-3333333.*AMZN Mktp DE.*AAAAABBBBBCCCCCD.*.*AMAZON PAYMENTS EUROPE S.C.A..*,19,99
    description AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND | Amazon 111-2222222-3333333
    comment type:%buchungstext, payee:AMAZON EU S.A R.L. NIEDERLASSUNG DEUTSCHLAND, order:111-2222222-3333333, ref:AAAAABBBBBCCCCCD
    account1    Expenses:Unterhaltung:Multimedia:Musik:Amazon                   

"""
        actual, account = gen_amazon_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Unterhaltung:Multimedia:Musik:Amazon', account)  # add assertion here

    def test_gen_amazon_rule_currency(self):
        config = {
            'amazon': {
                'if_format': [
                    '{order}.*Amazon.de{ref}AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
                    '{order}.*Amazon .Mktplce{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                    '{order}.*AMZN Mktp DE{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                ],
                'payee': 'AMAZON PAYMENTS EUROPE S.C.A.',
            },
        }
        rule = {
            'order': '111-2222222-3333333',
            'account': 'Expenses:Unterhaltung:Multimedia:Musik:Amazon',
            'payee': 'AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
            'ref': 'AAAAABBBBBCCCCCD',
            'amount': 19.99,
            'currency': 'EUR'
        }
        expected = """
if 111-2222222-3333333.*Amazon.de.*AAAAABBBBBCCCCCD.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND.*, 19,99,EUR
111-2222222-3333333.*Amazon.de.*AAAAABBBBBCCCCCD.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND.*,19,99,EUR
111-2222222-3333333.*Amazon .Mktplce.*AAAAABBBBBCCCCCD.*AMAZON PAYMENTS EUROPE S.C.A..*, 19,99,EUR
111-2222222-3333333.*Amazon .Mktplce.*AAAAABBBBBCCCCCD.*AMAZON PAYMENTS EUROPE S.C.A..*,19,99,EUR
111-2222222-3333333.*AMZN Mktp DE.*AAAAABBBBBCCCCCD.*AMAZON PAYMENTS EUROPE S.C.A..*, 19,99,EUR
111-2222222-3333333.*AMZN Mktp DE.*AAAAABBBBBCCCCCD.*AMAZON PAYMENTS EUROPE S.C.A..*,19,99,EUR
    description AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND | Amazon 111-2222222-3333333
    comment type:%buchungstext, payee:AMAZON EU S.A R.L. NIEDERLASSUNG DEUTSCHLAND, order:111-2222222-3333333, ref:AAAAABBBBBCCCCCD
    account1    Expenses:Unterhaltung:Multimedia:Musik:Amazon                   

"""
        actual, account = gen_amazon_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Unterhaltung:Multimedia:Musik:Amazon', account)  # add assertion here

    def test_gen_amazon_rule_income(self):
        config = {
            'amazon': {
                'if_format': [
                    '{order}.*Amazon.de{ref}AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
                    '{order}.*Amazon .Mktplce{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                    '{order}.*AMZN Mktp DE{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                ],
                'payee': 'AMAZON PAYMENTS EUROPE S.C.A.',
            },
        }
        rule = {
            'order': '111-2222222-3333333',
            'account': 'Income:Gutschrift:Amazon',
            'payee': 'AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
            'ref': 'AAAAABBBBBCCCCCD',
            'amount': 19.99,
            'income': True,
        }
        expected = """
if 111-2222222-3333333.*Amazon.de.*AAAAABBBBBCCCCCD.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND.*, -19,99
111-2222222-3333333.*Amazon.de.*AAAAABBBBBCCCCCD.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND.*,-19,99
111-2222222-3333333.*Amazon .Mktplce.*AAAAABBBBBCCCCCD.*AMAZON PAYMENTS EUROPE S.C.A..*, -19,99
111-2222222-3333333.*Amazon .Mktplce.*AAAAABBBBBCCCCCD.*AMAZON PAYMENTS EUROPE S.C.A..*,-19,99
111-2222222-3333333.*AMZN Mktp DE.*AAAAABBBBBCCCCCD.*AMAZON PAYMENTS EUROPE S.C.A..*, -19,99
111-2222222-3333333.*AMZN Mktp DE.*AAAAABBBBBCCCCCD.*AMAZON PAYMENTS EUROPE S.C.A..*,-19,99
    description AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND | Amazon 111-2222222-3333333
    comment type:%buchungstext, payee:AMAZON EU S.A R.L. NIEDERLASSUNG DEUTSCHLAND, order:111-2222222-3333333, ref:AAAAABBBBBCCCCCD
    account1    Income:Gutschrift:Amazon                                        

"""
        actual, account = gen_amazon_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Income:Gutschrift:Amazon', account)  # add assertion here


if __name__ == '__main__':
    unittest.main()
