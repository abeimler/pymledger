import unittest
from string import Template

from pymledger.HledgerRules import gen_amazon_rules_content

amazon_rules_template = Template(""";;do not change, generated file from amazon.csv.rules template

$rules""")


class HledgerRulesGenAmazonRulesContentTestCase(unittest.TestCase):
    def test_gen_amazon_rules_content_empty(self):
        config = {}
        expected = """;;do not change, generated file from amazon.csv.rules template

"""
        self.assertEqual(expected, gen_amazon_rules_content(config,  amazon_rules_template))  # add assertion here

    def test_gen_amazon_rules_content_empty_rules(self):
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
        expected = """;;do not change, generated file from amazon.csv.rules template

"""
        self.assertEqual(expected, gen_amazon_rules_content(config, amazon_rules_template))  # add assertion here

    def test_gen_amazon_rules_content_amazon_music_rule(self):
        config = {
            'amazon': {
                'if_format': [
                    '{order}.*Amazon.de{ref}AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
                    '{order}.*Amazon .Mktplce{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                    '{order}.*AMZN Mktp DE{ref}AMAZON PAYMENTS EUROPE S.C.A.',
                ],
                'payee': 'AMAZON PAYMENTS EUROPE S.C.A.',
            },
            'amazon_rules': [{
                'if': [
                    'Amazon Digital Svcs.*AMAZON MEDIA EU S.A R.L.',
                    'Amazon Music.*AMAZON MEDIA EU S.A R.L.',
                ],
                'description': 'Amazon Media Abo',
                'account': 'Expenses:Unterhaltung:Multimedia:Musik:Streaming:Abo:Amazon:Music',
            }]
        }
        expected = """;;do not change, generated file from amazon.csv.rules template


if Amazon Digital Svcs.*AMAZON MEDIA EU S.A R.L.
Amazon Music.*AMAZON MEDIA EU S.A R.L.
    description %beguenstigter_zahlungspflichtiger | Amazon Media Abo
    account1    Expenses:Unterhaltung:Multimedia:Musik:Streaming:Abo:Amazon:Music

"""
        self.assertEqual(expected, gen_amazon_rules_content(config,  amazon_rules_template))  # add assertion here


if __name__ == '__main__':
    unittest.main()
