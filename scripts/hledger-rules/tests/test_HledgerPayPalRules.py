import unittest

from pymledger.HledgerPayPalRules import gen_paypal_rule


class HledgerPayPalRulesGenPayPalRuleTestCase(unittest.TestCase):
    #maxDiff = None
    def test_gen_paypal_rule_empty(self):
        config = {}
        rule = {}
        expected = """"""
        actual, account = gen_paypal_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual(None, account)  # add assertion here

    def test_gen_paypal_rule_if_format(self):
        config = {
            'paypal': {
                'if_format': [
                    '{ref}.*PP.[0-9]+.PP.*{name}.*, Ihr Einkauf bei.*PayPal',
                    '{ref}.*PP.[0-9]+.PP.*{name}.*, Ihr Einkauf bei.*PAYPAL'
                ],
                'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
            },
        }
        rule = {
            'name': 'Steam',
            'account': 'Expenses:Hobbies:Gaming:Steam',
        }
        expected = """
if .*.*PP.[0-9]+.PP.*Steam.*, Ihr Einkauf bei.*PayPal
.*.*PP.[0-9]+.PP.*Steam.*, Ihr Einkauf bei.*PAYPAL
    description PayPal Europe S.a.r.l. et Cie S.C.A | PayPal Steam
    comment type:%buchungstext, payee:PayPal Europe S.a.r.l. et Cie S.C.A, name:Steam
    account1    Expenses:Hobbies:Gaming:Steam                                   

"""
        actual, account = gen_paypal_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Hobbies:Gaming:Steam', account)  # add assertion here

    def test_gen_paypal_rule_name(self):
        config = {
            'paypal': {
              'prefix': 'PP.[0-9]+.PP',
              'suffix': 'PayPal',
              'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
            },
        }
        rule = {
            'name': 'Steam',
            'account': 'Expenses:Hobbies:Gaming:Steam',
        }
        expected = """
if PP.[0-9]+.PP.*Steam.*.*.*PayPal
Steam.*.*.*PayPal
Steam.*PAYPAL.*.*
    description PayPal Europe S.a.r.l. et Cie S.C.A | PayPal Steam
    comment type:%buchungstext, payee:PayPal Europe S.a.r.l. et Cie S.C.A, name:Steam
    account1    Expenses:Hobbies:Gaming:Steam                                   

"""
        actual, account = gen_paypal_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Hobbies:Gaming:Steam', account)  # add assertion here

    def test_gen_paypal_rule_description(self):
        config = {
            'paypal': {
              'prefix': 'PP.[0-9]+.PP',
              'suffix': 'PayPal',
              'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
            },
        }
        rule = {
            'name': 'steampowered',
            'account': 'Expenses:Hobbies:Gaming:Steam',
            'description': 'Steam'
        }
        expected = """
if PP.[0-9]+.PP.*steampowered.*.*.*PayPal
steampowered.*.*.*PayPal
steampowered.*PAYPAL.*.*
    description PayPal Europe S.a.r.l. et Cie S.C.A | PayPal Steam
    comment type:%buchungstext, payee:PayPal Europe S.a.r.l. et Cie S.C.A, name:steampowered
    account1    Expenses:Hobbies:Gaming:Steam                                   

"""
        actual, account = gen_paypal_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Hobbies:Gaming:Steam', account)  # add assertion here

    def test_gen_paypal_rule_full_description(self):
        config = {
            'paypal': {
                'prefix': 'PP.[0-9]+.PP',
                'suffix': 'PayPal',
                'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
            },
        }
        rule = {
            'name': 'Google',
            'account': 'Expenses:Computer:Software:GooglePlayStore',
            'full_description': 'Google | Play Store'
        }
        expected = """
if PP.[0-9]+.PP.*Google.*.*.*PayPal
Google.*.*.*PayPal
Google.*PAYPAL.*.*
    description Google | Play Store
    comment type:%buchungstext, payee:PayPal Europe S.a.r.l. et Cie S.C.A, name:Google
    account1    Expenses:Computer:Software:GooglePlayStore                      

"""
        actual, account = gen_paypal_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Computer:Software:GooglePlayStore', account)  # add assertion here

    def test_gen_paypal_rule_payee(self):
        config = {
            'paypal': {
              'prefix': 'PP.[0-9]+.PP',
              'suffix': 'PayPal',
              'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
            },
        }
        rule = {
            'name': 'steampowered',
            'account': 'Expenses:Hobbies:Gaming:Steam',
            'description': 'Steam',
            'payee': 'PayPal Europe S.a.r.l., et Cie S.C.A'
        }
        expected = """
if PP.[0-9]+.PP.*steampowered.*.*.*PayPal
steampowered.*.*.*PayPal
steampowered.*PAYPAL.*.*
    description PayPal Europe S.a.r.l., et Cie S.C.A | PayPal Steam
    comment type:%buchungstext, payee:PayPal Europe S.a.r.l. et Cie S.C.A, name:steampowered
    account1    Expenses:Hobbies:Gaming:Steam                                   

"""
        actual, account = gen_paypal_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Hobbies:Gaming:Steam', account)  # add assertion here

    def test_gen_paypal_rule_no_payee(self):
        config = {
            'paypal': {
                'prefix': 'PP.[0-9]+.PP',
                'suffix': 'PayPal',
            },
        }
        rule = {
            'name': 'steampowered',
            'account': 'Expenses:Hobbies:Gaming:Steam',
            'description': 'Steam',
        }
        expected = """
if PP.[0-9]+.PP.*steampowered.*.*.*PayPal
steampowered.*.*.*PayPal
steampowered.*PAYPAL.*.*
    description %payee | PayPal Steam
    comment type:%buchungstext, payee:%payee, name:steampowered
    account1    Expenses:Hobbies:Gaming:Steam                                   

"""
        actual, account = gen_paypal_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Hobbies:Gaming:Steam', account)  # add assertion here

    def test_gen_paypal_rule_amount(self):
        config = {
            'paypal': {
              'prefix': 'PP.[0-9]+.PP',
              'suffix': 'PayPal',
              'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
            },
        }
        rule = {
            'name': 'steampowered',
            'account': 'Expenses:Hobbies:Gaming:Steam',
            'description': 'Steam',
            'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
            'amount': -19.99,
        }
        expected = """
if PP.[0-9]+.PP.*steampowered.*.*.*PayPal.*, -19,99
PP.[0-9]+.PP.*steampowered.*.*.*PayPal.*,-19,99
steampowered.*.*.*PayPal.*, -19,99
steampowered.*.*.*PayPal.*,-19,99
steampowered.*PAYPAL.*.*.*, -19,99
steampowered.*PAYPAL.*.*.*,-19,99
    description PayPal Europe S.a.r.l. et Cie S.C.A | PayPal Steam
    comment type:%buchungstext, payee:PayPal Europe S.a.r.l. et Cie S.C.A, name:steampowered
    account1    Expenses:Hobbies:Gaming:Steam                                   

"""
        actual, account = gen_paypal_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Hobbies:Gaming:Steam', account)  # add assertion here

    def test_gen_paypal_rule_currency(self):
        config = {
            'paypal': {
              'prefix': 'PP.[0-9]+.PP',
              'suffix': 'PayPal',
              'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
            },
        }
        rule = {
            'name': 'steampowered',
            'account': 'Expenses:Hobbies:Gaming:Steam',
            'description': 'Steam',
            'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
            'amount': -19.99,
            'currency': 'EUR'
        }
        expected = """
if PP.[0-9]+.PP.*steampowered.*.*.*PayPal.*, -19,99,EUR
PP.[0-9]+.PP.*steampowered.*.*.*PayPal.*,-19,99,EUR
steampowered.*.*.*PayPal.*, -19,99,EUR
steampowered.*.*.*PayPal.*,-19,99,EUR
steampowered.*PAYPAL.*.*.*, -19,99,EUR
steampowered.*PAYPAL.*.*.*,-19,99,EUR
    description PayPal Europe S.a.r.l. et Cie S.C.A | PayPal Steam
    comment type:%buchungstext, payee:PayPal Europe S.a.r.l. et Cie S.C.A, name:steampowered
    account1    Expenses:Hobbies:Gaming:Steam                                   

"""
        actual, account = gen_paypal_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Hobbies:Gaming:Steam', account)  # add assertion here

    def test_gen_paypal_rule_big_amount(self):
        config = {
            'paypal': {
              'prefix': 'PP.[0-9]+.PP',
              'suffix': 'PayPal',
              'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
            },
        }
        rule = {
            'name': 'MMS E-Commerce GmbH',
            'account': 'Expenses:Computer:Hardware:Saturn',
            'description': 'Saturn',
            'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
            'amount': -649.0,
        }
        expected = """
if PP.[0-9]+.PP.*MMS E-Commerce GmbH.*.*.*PayPal.*,-649
MMS E-Commerce GmbH.*.*.*PayPal.*,-649
MMS E-Commerce GmbH.*PAYPAL.*.*.*,-649
    description PayPal Europe S.a.r.l. et Cie S.C.A | PayPal Saturn
    comment type:%buchungstext, payee:PayPal Europe S.a.r.l. et Cie S.C.A, name:MMS E-Commerce GmbH
    account1    Expenses:Computer:Hardware:Saturn                               

"""
        actual, account = gen_paypal_rule(config, rule)
        self.assertEqual(expected, actual)  # add assertion here
        self.assertEqual('Expenses:Computer:Hardware:Saturn', account)  # add assertion here


if __name__ == '__main__':
    unittest.main()
