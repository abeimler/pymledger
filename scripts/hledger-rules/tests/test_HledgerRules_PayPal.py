import unittest
from string import Template

from pymledger.HledgerRules import gen_paypal_rules_content

paypal_rules_template = Template(""";;do not change, generated file from paypal.csv.rules template

$rules""")


class HledgerRulesGenPayPalRulesContentTestCase(unittest.TestCase):
    #maxDiff = None
    def test_gen_paypal_rules_content_empty(self):
        config = {}
        expected = """;;do not change, generated file from paypal.csv.rules template

"""
        self.assertEqual(expected, gen_paypal_rules_content(config,  paypal_rules_template))  # add assertion here

    def test_gen_paypal_rules_content_no_name(self):
        config = {
            'paypal': {
                'prefix': 'PP.6330.P',
                'suffix': 'PayPal',
                'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
            },
            'paypal_rules': [
                {
                    'account': 'Expenses:Hobbies:Gaming:GOG',
                }
            ]
        }
        expected = """;;do not change, generated file from paypal.csv.rules template

"""
        self.assertEqual(expected, gen_paypal_rules_content(config, paypal_rules_template))  # add assertion here

    def test_gen_paypal_rules_content_name(self):
        config = {
            'paypal': {
              'prefix': 'PP.6330.P',
              'suffix': 'PayPal',
              'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
            },
            'paypal_rules': [
                {
                    'name': 'GOG',
                    'description': 'GOG',
                    'account': 'Expenses:Hobbies:Gaming:GOG',
                }
            ]
        }
        expected = """;;do not change, generated file from paypal.csv.rules template


if PP.1234.PP.*GOG.*PayPal.*.*.*.*
GOG.*PayPal.*.*.*.*
GOG.*PAYPAL.*.*.*.*
    description %payee | PayPal GOG
    comment type:%buchungstext, payee:%payee, name:GOG
    account1    Expenses:Hobbies:Gaming:GOG                                     

"""
        self.assertEqual(expected, gen_paypal_rules_content(config,  paypal_rules_template))  # add assertion here

    def test_gen_paypal_rules_content_names(self):
        config = {
            'paypal': {
              'prefix': 'PP.6330.P',
              'suffix': 'PayPal',
              'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
            },
            'paypal_rules': [
                {
                    'name': [
                        'Steam',
                        'STEAM',
                        'steampowered'
                    ],
                    'description': 'Steam',
                    'account': 'Expenses:Hobbies:Gaming:Steam',
                }
            ]
        }
        expected = """;;do not change, generated file from paypal.csv.rules template


if PP.1234.PP.*Steam.*PayPal.*.*.*.*
Steam.*PayPal.*.*.*.*
Steam.*PAYPAL.*.*.*.*
PP.1234.PP.*STEAM.*PayPal.*.*.*.*
STEAM.*PayPal.*.*.*.*
STEAM.*PAYPAL.*.*.*.*
PP.1234.PP.*steampowered.*PayPal.*.*.*.*
steampowered.*PayPal.*.*.*.*
steampowered.*PAYPAL.*.*.*.*
    description %payee | PayPal Steam
    comment type:%buchungstext, payee:%payee, name:Steam
    account1    Expenses:Hobbies:Gaming:Steam                                   

"""
        self.assertEqual(expected, gen_paypal_rules_content(config,  paypal_rules_template))  # add assertion here

    def test_gen_paypal_rules_content_ref(self):
        config = {
            'paypal': {
              'prefix': 'PP.6330.P',
              'suffix': 'PayPal',
              'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
            },
            'paypal_rules': [
                {
                    'name': [
                        'Google',
                    ],
                    'description': 'Google Play Store',
                    'account': 'Expenses:Computer:Software:GooglePlayStore',
                    'ref': '123456789',
                }
            ]
        }
        expected = """;;do not change, generated file from paypal.csv.rules template


if PP.1234.PP.*Google.*PayPal.*123456789.*.*
Google.*PayPal.*123456789.*.*
Google.*PAYPAL.*123456789.*.*
    description %payee | PayPal Google Play Store
    comment type:%buchungstext, payee:%payee, name:Google
    account1    Expenses:Computer:Software:GooglePlayStore                      

"""
        self.assertEqual(expected, gen_paypal_rules_content(config,  paypal_rules_template))  # add assertion here

    def test_gen_paypal_rules_content_payee(self):
        config = {
            'paypal': {
              'prefix': 'PP.6330.P',
              'suffix': 'PayPal',
              'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
            },
            'paypal_rules': [
                {
                    'name': [
                        'Google',
                    ],
                    'description': 'Google Play Store',
                    'account': 'Expenses:Computer:Software:GooglePlayStore',
                    'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
                }
            ]
        }
        expected = """;;do not change, generated file from paypal.csv.rules template


if PP.1234.PP.*Google.*PayPal.*.*.*.*
Google.*PayPal.*.*.*.*
Google.*PAYPAL.*.*.*.*
    description PayPal Europe S.a.r.l. et Cie S.C.A | PayPal Google Play Store
    comment type:%buchungstext, payee:PayPal Europe S.a.r.l. et Cie S.C.A, name:Google
    account1    Expenses:Computer:Software:GooglePlayStore                      

"""
        self.assertEqual(expected, gen_paypal_rules_content(config,  paypal_rules_template))  # add assertion here

    def test_gen_paypal_rules_content_payee(self):
        config = {
            'paypal': {
              'prefix': 'PP.6330.P',
              'suffix': 'PayPal',
              'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
            },
            'paypal_rules': [
                {
                    'name': [
                        'Google',
                    ],
                    'description': 'Google Play Store',
                    'account': 'Expenses:Computer:Software:GooglePlayStore',
                    'payee': 'PayPal Europe S.a.r.l. et Cie S.C.A',
                }
            ]
        }
        expected = """;;do not change, generated file from paypal.csv.rules template


if PP.1234.PP.*Google.*PayPal.*.*.*.*
Google.*PayPal.*.*.*.*
Google.*PAYPAL.*.*.*.*
    description PayPal Europe S.a.r.l. et Cie S.C.A | PayPal Google Play Store
    comment type:%buchungstext, payee:PayPal Europe S.a.r.l. et Cie S.C.A, name:Google
    account1    Expenses:Computer:Software:GooglePlayStore                      

"""
        self.assertEqual(expected, gen_paypal_rules_content(config,  paypal_rules_template))  # add assertion here


if __name__ == '__main__':
    unittest.main()
