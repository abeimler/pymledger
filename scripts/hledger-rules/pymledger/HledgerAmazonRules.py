import csv
import datetime
import re

import yaml

from pymledger import Const, HledgerTemplates as Templates, utils
from pymledger.HledgerRules import gen_rule, sort_rule_element
from pymledger.HledgerUtils import amount_to_rule_string, string_to_amount_value, extend_if_conds_with_amount


def gen_amazon_rule(config, rule, filename_yaml=None):
    order = rule['order'] if 'order' in rule else ''
    ref = ".*{}.*".format(rule['ref']) if 'ref' in rule and rule['ref'] else '.*'
    description = rule['description'] if 'description' in rule else ''
    full_description = rule['full_description'] if 'full_description' in rule else ''
    account = rule['account'] if 'account' in rule else ''
    amount = amount_to_rule_string(rule['amount']) if 'amount' in rule and rule['amount'] else None
    payee = rule['payee'] if 'payee' in rule else Const.PAYEE_AMAZON
    currency = rule['currency'] if 'currency' in rule else None
    income = rule['income'] if 'income' in rule else False

    ref = re.sub(r'\s+', ' ', ref)
    description = re.sub(r'\s+', ' ', description)
    account = re.sub(r'\s+', ' ', account)
    ret_account = None

    if not description:
        description = order

    is_disabled = ('example' in rule and rule['example']) or ('enable' in rule and not rule['enable']) or (
            'disabled' in rule and rule['disabled'])
    pre = ';' if is_disabled else ''
    if ((not order and not ref) or not account):
        utils.print_error("order/ref and account are required in yaml: {}".format(filename_yaml))
        return '', ret_account

    if 'amazon' in config and 'if_format' in config['amazon']:
        if_conds = []
        for if_format in config['amazon']['if_format']:
            if_conds.append(if_format.format(order=order, ref=ref).strip())

        if_conds = extend_if_conds_with_amount(if_conds, rule)

        if not is_disabled:
            ret_account = account

        if 'payee' in rule:
            payee = rule['payee']
        elif 'payee' in config['amazon'] and config['amazon']['payee']:
            payee = config['amazon']['payee']

        new_description=description.format(order=order, ref=rule.get('ref', ''))

        full_description = Templates.AMAZON_DESCRIPTION_FORMAT.format(description=new_description.strip())
        if payee:
            full_description = Templates.AMAZON_DESCRIPTION_PAYEE_FORMAT.format(payee=payee,
                                                                                description=new_description.strip())
        if 'full_description' in rule:
            full_description = rule['full_description'] if 'full_description' in rule else ''

        tags = []
        if 'order' in rule:
            tags.append("order:{}".format(rule['order'].replace(',', '').replace('\n', ' ').strip()))
        if 'ref' in rule and rule['ref']:
            tags.append("ref:{}".format(rule['ref'].replace(',', '').replace('\n', ' ').strip()))

        return gen_rule(if_conds, full_description, account1=account, pre=pre, tags=tags, payee=payee), ret_account

    return '', ret_account


def gen_amazon_rules(config, filename_yaml, filename_rules, year='', month=''):
    now = datetime.datetime.now()
    ret = set()
    with open(filename_yaml) as data_file:
        data = yaml.load(data_file, Loader=yaml.FullLoader)
        with open(filename_rules, 'w') as rules_file:
            rules = ''
            if data:
                for rule in data:
                    amazon_rules, account = gen_amazon_rule(config, rule, filename_yaml)
                    rules = rules + amazon_rules
                    if account:
                        ret.add(account)
            rules_file.write(Templates.AMAZON_RULES_CONTENT_TEMPLATE.substitute(rules=rules, year=year, month=month,
                                                                                now=now.strftime('%Y-%m-%d %H:%M:%S')))
    return ret


def gen_amazon_rule_template(row):
    ret = None
    if ('AMZN Mktp DE' in row[Const.ROW_NAME_USE] or 'Amazon.de' in row[Const.ROW_NAME_USE]) and (
            'AMAZON PAYMENTS' in row[Const.ROW_NAME_RECIPIENT] or 'AMAZON EU' in row[Const.ROW_NAME_RECIPIENT]):
        match_data = re.match(r'^([0-9\-]+)\s+(AMZN Mktp DE|Amazon.de|Amazon.com|Amazon .Mktplce)\s+(\S+)\s*$',
                              row[Const.ROW_NAME_USE])
        if match_data:
            group_data = match_data.groups()
            order = group_data[0]
            ref = group_data[2]
            ret = {'order': order, 'ref': ref, 'account': Const.EXPENSE_AMAZON_UNKNOWN_ACCOUNT,
                   'amount': string_to_amount_value(row[Const.ROW_NAME_VALUE]),
                   'payee': row[Const.ROW_NAME_RECIPIENT].strip()}
            # if not row[ROW_NAME_RECIPIENT].strip().startswith(PAYEE_AMAZON):
            #  dat['payee']=row[ROW_NAME_RECIPIENT].strip()
            if row[Const.ROW_NAME_CURRENCY] != Const.CURRENCY:
                ret['currency'] = row[Const.ROW_NAME_CURRENCY]
    return ret


def gen_amazon_rules_template(filename_csv, filename_yaml, year, month):
    data = []
    count = 0
    with open(filename_csv, 'r', newline='') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=Const.CSV_DELIMITER, quotechar=Const.CSV_QUOTECHAR)
        for row in reader:
            if ".{:02}.{:02}".format(month, year - 2000) in row[Const.ROW_NAME_BOOKINGDATE] and (
                    'AMZN Mktp DE' in row[Const.ROW_NAME_USE] or 'Amazon.de' in row[Const.ROW_NAME_USE]) and (
                    'AMAZON PAYMENTS' in row[Const.ROW_NAME_RECIPIENT] or 'AMAZON EU' in row[Const.ROW_NAME_RECIPIENT]):
                skip = False
                for ignore in Const.IGNORE_AMAZONS:
                    if re.search(ignore, row[Const.ROW_NAME_USE]) or re.search(ignore.upper(),
                                                                               row[Const.ROW_NAME_USE].upper()):
                        skip = True
                if not skip:
                    dat = gen_amazon_rule_template(row)
                    if dat:
                        data.append(dat)
            count = count + 1
    data.sort(key=sort_rule_element)
    if data:
        utils.print_succ("amazon rules find {} in {} rows for {:04}-{:02}".format(len(data), count, year, month))
        with open(filename_yaml, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)
    else:
        utils.print_succ("amazon: No entries found for {:04}-{:02}".format(year, month))
    return data
