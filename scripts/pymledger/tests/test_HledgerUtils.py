import unittest

from pymledger.HledgerUtils import amount_to_journal_amount_string, amount_to_rule_string, string_to_amount_value


class HledgerUtilsAmountToJournalString(unittest.TestCase):
    def test_7digits(self):
        self.assertEqual('1000000,00', amount_to_journal_amount_string(1000000.0))

    def test_3decimal(self):
        self.assertEqual('100,987', amount_to_journal_amount_string(100.987))

    def test_3digits(self):
        self.assertEqual('100,00', amount_to_journal_amount_string(100.0))

    def test_2digits(self):
        self.assertEqual('99,99', amount_to_journal_amount_string(99.99))

    def test_1digits(self):
        self.assertEqual('1,01', amount_to_journal_amount_string(1.01))

    def test_3digits2(self):
        self.assertEqual('649,00', amount_to_journal_amount_string(649.00))

class HledgerUtilsAmountToRuleString(unittest.TestCase):
    def test_str_with_dot_decimal_mark(self):
        self.assertEqual('100,00', amount_to_rule_string('100.00'))

    def test_str_with_comma_decimal_mark(self):
        self.assertEqual('100,00', amount_to_rule_string('100,00'))

    def test_int_3digits(self):
        self.assertEqual('100,00', amount_to_rule_string(100))

    def test_int_2digits(self):
        self.assertEqual('99,00', amount_to_rule_string(99))

    def test_int_1digits(self):
        self.assertEqual(amount_to_rule_string(1), '1,00')

    def test_float_3digits(self):
        self.assertEqual('100,987', amount_to_rule_string(100.987))

    def test_float_2digits(self):
        self.assertEqual('99,99', amount_to_rule_string(99.99))

    def test_float_1digits(self):
        self.assertEqual('9,99', amount_to_rule_string(9.99))

    def test_float_flow(self):
        self.assertEqual('0,01', amount_to_rule_string(0.01))

    def test_float_zero(self):
        self.assertEqual('0,00', amount_to_rule_string(0.0))

    def test_float_3digits2(self):
        self.assertEqual('649,00', amount_to_rule_string(649.0))


class HledgerUtilsStringToAmountValue(unittest.TestCase):
    def test_str_with_dot_decimal_mark(self):
        self.assertEqual(100.00, string_to_amount_value('100.00'))

    def test_str_with_comma_decimal_mark(self):
        self.assertEqual(100.00, string_to_amount_value('100,00'))

    def test_int_3digits(self):
        self.assertEqual(100.00, string_to_amount_value('100'))

    def test_int_2digits(self):
        self.assertEqual(99.99, string_to_amount_value('99,99'))

    def test_int_1digits(self):
        self.assertEqual(1.1, string_to_amount_value('1,1'))

    def test_int_1digits_2(self):
        self.assertEqual(1.01, string_to_amount_value('1,01'))


if __name__ == '__main__':
    unittest.main()
