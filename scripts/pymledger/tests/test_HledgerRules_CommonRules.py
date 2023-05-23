import unittest

from pymledger.HledgerRules import gen_common_rules


class HledgerRulesGenCommonRulesTestCase(unittest.TestCase):
    def test_gen_common_rules_empty(self):
        rules_config = []
        expected = """"""
        self.assertEqual(expected, gen_common_rules(rules_config))  # add assertion here

    def test_gen_common_rules_if_rule(self):
        rules_config = [
            {
                'if': 'KARTENZAHLUNG',
                'description': 'Kartenzahlung %verwendungszweck',
                'account': 'Expenses:unknown:%beguenstigter_zahlungspflichtiger',
            }
        ]
        expected = """
if KARTENZAHLUNG
    description %beguenstigter_zahlungspflichtiger | Kartenzahlung %verwendungszweck
    account1    Expenses:unknown:%beguenstigter_zahlungspflichtiger             

"""
        self.assertEqual(expected, gen_common_rules(rules_config))  # add assertion here

    def test_gen_common_rules_ifs_rule(self):
        rules_config = [
            {
                'if': [
                    'Amazon.de.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND',
                    'Amazon.Mktplce.*AMAZON PAYMENTS EUROPE S.C.A.',
                    'AMZN Mktp DE.*AMAZON PAYMENTS EUROPE S.C.A.',
                ],
                'description': 'Amazon %verwendungszweck',
                'account': 'Expenses:unknown:Amazon',
            }
        ]
        expected = """
if Amazon.de.*AMAZON EU S.A R.L., NIEDERLASSUNG DEUTSCHLAND
Amazon.Mktplce.*AMAZON PAYMENTS EUROPE S.C.A.
AMZN Mktp DE.*AMAZON PAYMENTS EUROPE S.C.A.
    description %beguenstigter_zahlungspflichtiger | Amazon %verwendungszweck
    account1    Expenses:unknown:Amazon                                         

"""
        self.assertEqual(expected, gen_common_rules(rules_config))  # add assertion here

    def test_gen_common_rules_name(self):
        rules_config = [
            {
                'name': 'LIDL',
                'description': 'Einkaufen Lidl',
                'account': 'Expenses:Lebensmittel:Einkaufen:Lidl',
            }
        ]
        expected = """
if KARTENZAHLUNG.*LIDL
LASTSCHRIFT.*LIDL
RECHNUNG.*LIDL
    description %beguenstigter_zahlungspflichtiger | Einkaufen Lidl
    account1    Expenses:Lebensmittel:Einkaufen:Lidl                            

"""
        self.assertEqual(expected, gen_common_rules(rules_config))  # add assertion here

    def test_gen_common_rules_name_with_space(self):
        rules_config = [
            {
                'name': 'Rewe GmbH',
                'description': 'Einkaufen Rewe',
                'account': 'Expenses:Lebensmittel:Einkaufen:Rewe',
            }
        ]
        expected = """
if KARTENZAHLUNG.*Rewe GmbH
LASTSCHRIFT.*Rewe GmbH
RECHNUNG.*Rewe GmbH
    description %beguenstigter_zahlungspflichtiger | Einkaufen Rewe
    account1    Expenses:Lebensmittel:Einkaufen:Rewe                            

"""
        self.assertEqual(expected, gen_common_rules(rules_config))  # add assertion here

    def test_gen_common_rules_names(self):
        rules_config = [
            {
                'name': ['REWE', 'REWE SAGT DANKE', 'DANKE REWE IHR KAUFPARK'],
                'description': 'Einkaufen Rewe',
                'account': 'Expenses:Lebensmittel:Einkaufen:Rewe',
            }
        ]
        expected = """
if KARTENZAHLUNG.*REWE
LASTSCHRIFT.*REWE
RECHNUNG.*REWE
KARTENZAHLUNG.*REWE SAGT DANKE
LASTSCHRIFT.*REWE SAGT DANKE
RECHNUNG.*REWE SAGT DANKE
KARTENZAHLUNG.*DANKE REWE IHR KAUFPARK
LASTSCHRIFT.*DANKE REWE IHR KAUFPARK
RECHNUNG.*DANKE REWE IHR KAUFPARK
    description %beguenstigter_zahlungspflichtiger | Einkaufen Rewe
    account1    Expenses:Lebensmittel:Einkaufen:Rewe                            

"""
        self.assertEqual(expected, gen_common_rules(rules_config))  # add assertion here

    def test_gen_common_rules_invoice_name(self):
        rules_config = [
            {
                'invoice_name': 'UNITYMEDIA',
                'description': 'Unitymedia (Vodafone) Internet',
                'account': 'Expenses:Telekommunikation:Online-Dienste:Internet:Unitymedia',
            }
        ]
        expected = """
if RECHNUNG.*UNITYMEDIA
    description %beguenstigter_zahlungspflichtiger | Unitymedia (Vodafone) Internet
    account1    Expenses:Telekommunikation:Online-Dienste:Internet:Unitymedia   

"""
        self.assertEqual(expected, gen_common_rules(rules_config))  # add assertion here

    def test_gen_common_rules_payment_name(self):
        rules_config = [
            {
                'payment_name': 'LIDL',
                'description': 'Einkaufen Lidl',
                'account': 'Expenses:Lebensmittel:Einkaufen:Lidl',
            }
        ]
        expected = """
if KARTENZAHLUNG.*LIDL
LASTSCHRIFT.*LIDL
RECHNUNG.*LIDL
    description %beguenstigter_zahlungspflichtiger | Einkaufen Lidl
    account1    Expenses:Lebensmittel:Einkaufen:Lidl                            

"""
        self.assertEqual(expected, gen_common_rules(rules_config))  # add assertion here

    def test_gen_common_rules_payee_description(self):
        rules_config = [
            {
                'if': 'ENTGELTABSCHLUSS.*Entgeltabrechnung',
                'account': 'Expenses:Sonstiges:Bankgebuehren',
                'payee_description': 'Sparkasse | Sparkasse Entgeltabrechnung',
            }
        ]
        expected = """
if ENTGELTABSCHLUSS.*Entgeltabrechnung
    description Sparkasse | Sparkasse Entgeltabrechnung
    account1    Expenses:Sonstiges:Bankgebuehren                                

"""
        self.assertEqual(expected, gen_common_rules(rules_config))  # add assertion here

    def test_gen_common_rules_credit_note(self):
        rules_config = [
            {
                'credit_note': 'AMZ.*AMAZON PAYMENTS',
                'account': 'Income:Sonstiges:Gutschrift:Amazon:Rueckerstattung',
                'description': 'Amazon Rueckerstattung',
            }
        ]
        expected = """
if GUTSCHR.*AMZ.*AMAZON PAYMENTS
    description %beguenstigter_zahlungspflichtiger | Amazon Rueckerstattung
    account1    assets:bank:checking                                            
    account2    Income:Sonstiges:Gutschrift:Amazon:Rueckerstattung              
    amount      %amount                                                         

"""
        self.assertEqual(expected, gen_common_rules(rules_config))  # add assertion here


if __name__ == '__main__':
    unittest.main()
