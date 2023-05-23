import unittest

from pymledger.HledgerRules import gen_rule


class HledgerRulesGenRuleTestCase(unittest.TestCase):
    def test_gen_rule_empty(self):
        self.assertEqual(gen_rule([],  ''), """""")  # add assertion here

    def test_gen_rule_empty_only_comment(self):
        self.assertEqual(gen_rule([],  '', file_comment='Test comment'), """;;Test comment
""")  # add assertion here

    def test_gen_rule_if_rule_with_account(self):
        if_conds=['Test', 'TEST', 'test']
        expected = """
if Test
TEST
test
    description Test description
    account1    expenses:Test                                                   

"""
        self.assertEqual(expected, gen_rule(if_conds,  'Test description', account='expenses:Test'))  # add assertion here

    def test_gen_rule_if_rule_with_account2(self):
        if_conds=['Test', 'TEST', 'test']
        expected = """
if Test
TEST
test
    description Test description
    account1    expenses:Test                                                   
    account2    assets:Test                                                     

"""
        self.assertEqual(expected, gen_rule(if_conds, 'Test description', account1='expenses:Test', account2='assets:Test'))  # add assertion here

    def test_gen_rule_if_rule_income(self):
        if_conds=['Test', 'TEST', 'test']
        expected = """
if Test
TEST
test
    description Test description
    account1    expenses:Test                                                   
    account2    assets:Test                                                     
    amount      %amount                                                         

"""
        self.assertEqual(expected, gen_rule(if_conds,  'Test description', account1='expenses:Test', account2='assets:Test', income=True))  # add assertion here


    def test_gen_rule_if_rule_with_file_comment(self):
        if_conds=['Test', 'TEST', 'test']
        self.assertEqual(gen_rule(if_conds,  'Test description', account='expenses:Test', file_comment='test comment'), """;;test comment
if Test
TEST
test
    description Test description
    account1    expenses:Test                                                   

""")  # add assertion here

    def test_gen_rule_if_rule_with_comment(self):
        if_conds=['Test', 'TEST', 'test']
        self.assertEqual(gen_rule(if_conds,  'Test description', account='expenses:Test', comment='test comment'), """
if Test
TEST
test
    description Test description
    comment test comment
    account1    expenses:Test                                                   

""")  # add assertion here

    def test_gen_rule_if_rule_with_tags(self):
        if_conds=['Test', 'TEST', 'test']
        self.assertEqual(gen_rule(if_conds,  'Test description', account='expenses:Test', tags=['t1', 't2']), """
if Test
TEST
test
    description Test description
    comment type:%buchungstext, payee:%payee, t1:, t2:
    account1    expenses:Test                                                   

""")  # add assertion here

    def test_gen_rule_if_rule_with_tags_colon(self):
        if_conds=['Test', 'TEST', 'test']
        self.assertEqual(gen_rule(if_conds,  'Test description', account='expenses:Test', tags=['t1:', 't2:']), """
if Test
TEST
test
    description Test description
    comment type:%buchungstext, payee:%payee, t1:, t2:
    account1    expenses:Test                                                   

""")  # add assertion here

    def test_gen_rule_if_rule_with_tags_colon_value(self):
        if_conds=['Test', 'TEST', 'test']
        self.assertEqual(gen_rule(if_conds,  'Test description', account='expenses:Test', tags=['t1:', 't2:value']), """
if Test
TEST
test
    description Test description
    comment type:%buchungstext, payee:%payee, t1:, t2:value
    account1    expenses:Test                                                   

""")  # add assertion here

    def test_gen_rule_if_rule_with_tags_and_comment(self):
        if_conds=['Test', 'TEST', 'test']
        self.assertEqual(gen_rule(if_conds,  'Test description', account='expenses:Test', comment='test comment', tags=['t1:', 't2:value']), """
if Test
TEST
test
    description Test description
    comment test comment type:%buchungstext, payee:%payee, t1:, t2:value
    account1    expenses:Test                                                   

""")  # add assertion here

    def test_gen_rule_if_rule_with_tags_comment_and_code(self):
        if_conds=['Test', 'TEST', 'test']
        self.assertEqual(gen_rule(if_conds,  'Test description', account='expenses:Test', comment='test comment', code='123456', tags=['t1:', 't2:value']), """
if Test
TEST
test
    description Test description
    comment test comment type:%buchungstext, payee:%payee, t1:, t2:value
    code 123456
    account1    expenses:Test                                                   

""")  # add assertion here

    def test_gen_rule_if_rule_with_comment_and_code(self):
        if_conds = ['Test', 'TEST', 'test']
        self.assertEqual(
            gen_rule(if_conds, 'Test description', account='expenses:Test', comment='test comment', code='123456'), """
if Test
TEST
test
    description Test description
    comment test comment
    code 123456
    account1    expenses:Test                                                   

""")  # add assertion here

    def test_gen_rule_if_rule_with_code(self):
        if_conds=['Test', 'TEST', 'test']
        self.assertEqual(gen_rule(if_conds,  'Test description', account='expenses:Test', code='123456'), """
if Test
TEST
test
    description Test description
    code 123456
    account1    expenses:Test                                                   

""")  # add assertion here

    def test_gen_rule_if_rule_with_tags_and_code(self):
        if_conds = ['Test', 'TEST', 'test']
        self.assertEqual(
            gen_rule(if_conds, 'Test description', account='expenses:Test', code='123456',tags=['t1:', 't2:value']), """
if Test
TEST
test
    description Test description
    comment type:%buchungstext, payee:%payee, t1:, t2:value
    code 123456
    account1    expenses:Test                                                   

""")  # add assertion here

    def test_gen_rule_if_rule_with_tags_comment_code_and_prefix(self):
        if_conds=['Test', 'TEST', 'test']
        self.assertEqual(gen_rule(if_conds,  'Test description', pre=';', account='expenses:Test', comment='test comment', code='123456', tags=['t1:', 't2:value']), """
;if Test
;TEST
;test
;    description Test description
;    comment test comment type:%buchungstext, payee:%payee, t1:, t2:value
;    code 123456
;    account1    expenses:Test                                                   

""")  # add assertion here


if __name__ == '__main__':
    unittest.main()
