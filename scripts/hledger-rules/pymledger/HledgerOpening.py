import os

import yaml

from pymledger import Const, utils, HledgerTemplates as Templates
from pymledger.HledgerUtils import amount_to_journal_amount_string


def get_opening(year, month, opening_data, status='', cl=False):
    opening_month = ''
    if opening_data:
        opening_status = status + ' ' if status else ''
        description = opening_status + Templates.OPENING_DESCRIPTION_FORMAT.format(
            year=year) if cl else opening_status + Templates.NON_CL_OPENING_DESCRIPTION_FORMAT.format(year=year)
        opening_month = "{:04}-{:02}-01 {}\n".format(year, month, description)
        for opening in opening_data:
            is_budget = ('budget' in opening and opening['budget']) or ('virtual' in opening and opening['virtual'])
            if 'account' in opening:
                account_name = opening['account'].strip()
                if is_budget:
                    account_name = Templates.BUDGET_ACCOUNT_FORMAT.format(opening['account'].strip())
                currency = ''
                amount = ''
                if 'amount' in opening:
                    amount = amount_to_journal_amount_string(opening['amount'])
                    currency = opening.get('currency', Const.CURRENCY)
                opening_month = opening_month + Templates.JOURNAL_ENTRY_FORMAT.format(account=account_name,
                                                                                      amount=amount, currency=currency)
        opening_month = opening_month + "    {}\n".format(Const.OPENING_ACCOUNT)
    return opening_month


def get_opening_from_yml_file(year, month, opening_yaml_filename, status='', cl=False):
    if os.path.exists(opening_yaml_filename):
        utils.print_verbose("read opening month yml: {}".format(opening_yaml_filename))
        with open(opening_yaml_filename, 'r') as opening_month_yaml_file:
            opening_data = yaml.safe_load(opening_month_yaml_file)
            return get_opening(year, month, opening_data, status, cl)
    return ''
