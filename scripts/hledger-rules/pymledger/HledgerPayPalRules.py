import csv
import datetime
import re

import yaml

from pymledger import Const, utils, HledgerTemplates as Templates
from pymledger.HledgerRules import gen_rule, sort_rule_element
from pymledger.HledgerUtils import amount_to_rule_string, string_to_amount_value, extend_if_conds_with_amount


def gen_paypal_rule(config, rule, filename_yaml=None):
    name = rule['name'] if 'name' in rule else ''
    description = rule['description'] if 'description' in rule else ''
    account = rule['account'] if 'account' in rule else ''
    ref = rule['ref'] if 'ref' in rule and rule['ref'] else '.*'
    payee = rule['payee'] if 'payee' in rule else Const.PAYEE_PAYPAL
    full_description = rule['full_description'] if 'full_description' in rule else ''
    amount = amount_to_rule_string(rule['amount']) if 'amount' in rule and rule['amount'] else None
    currency = rule['currency'] if 'currency' in rule and rule['currency'] else None
    income = rule['income'] if 'income' in rule and rule['income'] else False

    description = re.sub(r'\s+', ' ', description)
    account = re.sub(r'\s+', ' ', account)

    if not description:
        description = name

    ret_account = None

    is_disabled = ('example' in rule and rule['example']) or ('enable' in rule and not rule['enable']) or (
            'disabled' in rule and rule['disabled'])
    pre = ';' if is_disabled else ''

    if not name and not ref and not amount and not currency:
        utils.print_error("name, ref, amount or currency are required in yaml: {}".format(filename_yaml))
        return '', None
    if not account:
        utils.print_error("account is required in yaml: {}".format(filename_yaml))
        return '', None

    if not is_disabled:
        ret_account = account

    if 'payee' in rule:
        payee = rule['payee']
    elif 'payee' in config['paypal'] and config['paypal']['payee']:
        payee = config['paypal']['payee']

    if payee:
        full_description = Templates.PAYPAL_DESCRIPTION_PAYEE_FORMAT.format(description=description.strip(),
                                                                            payee=payee)
    else:
        full_description = Templates.PAYPAL_DESCRIPTION_FORMAT.format(description=description.strip())
    if 'full_description' in rule:
        full_description = rule['full_description']

    if_conds = []
    if 'if_format' in config['paypal'] and config['paypal']['if_format']:
        for if_format in config['paypal']['if_format']:
            if_conds.append(if_format.format(ref=ref, name=name))
    else:
        if_conds = [
            "{}.*{}.*{}.*{}".format(Const.PAYPAL_PREFIX, name, ref, Const.PAYPAL_SUFFIX),
            "{}.*{}.*{}".format(name, ref, Const.PAYPAL_SUFFIX),
            "{}.*{}.*{}".format(name, Const.ALT_PAYPAL_SUFFIX, ref),
        ]

    if_conds = extend_if_conds_with_amount(if_conds, rule)

    code = None
    tags = []
    if 'name' in rule:
        tags.append("name:{}".format(rule['name'].replace(',', '').replace('\n', ' ').strip()))
    if 'ref' in rule and rule['ref']:
        tags.append("ref:{}".format(rule['ref'].replace(',', '').replace('\n', ' ').strip()))
        code = rule['ref'].strip()

    rule = gen_rule(if_conds, description=full_description, account1=account, pre=pre, tags=tags, code=code,
                    payee=payee)

    return rule, ret_account


def gen_paypal_rules(config, filename_yaml, filename_rules, year='', month=''):
    now = datetime.datetime.now()
    ret = set()
    with open(filename_yaml) as data_file:
        data = yaml.load(data_file, Loader=yaml.FullLoader)
        with open(filename_rules, 'w') as rules_file:
            rules = ''
            if data:
                for rule in data:
                    rule, account = gen_paypal_rule(config, rule, filename_yaml)
                    if rule:
                        rules = rules + rule
                        ret.add(account)

            rules_file.write(Templates.PAYPAL_RULES_CONTENT_TEMPLATE.substitute(rules=rules, year=year, month=month,
                                                                                now=now.strftime('%Y-%m-%d %H:%M:%S')))
    return ret


def gen_paypal_rule_template(row):
    ret = None
    if (Const.PAYPAL_PREFIX in row[Const.ROW_NAME_USE] or Const.ALT_PAYPAL_SUFFIX in row[
        Const.ROW_NAME_REFERENCE] or Const.ALT_PAYPAL_SUFFIX in row[Const.ROW_NAME_RECIPIENT] or Const.PAYPAL_SUFFIX in
            row[Const.ROW_NAME_RECIPIENT]):
        match_data = re.match(r'^(.*), Ihr Einkauf bei (.*)$', row[Const.ROW_NAME_USE])
        match_no_name_data = re.match(r'^.*\s*.\s*, Ihr Einkauf bei(.*)$', row[Const.ROW_NAME_USE])
        match_ref_data = re.match(r'^(\S*).*$', row[Const.ROW_NAME_USE])
        match_ref_2_data = re.match(r'^(\S*).*$', row[Const.ROW_NAME_REFERENCE])

        ref = None
        name = None
        description = None
        account = Const.EXPENSE_PAYPAL_UNKNOWN_ACCOUNT

        if match_ref_data:
            group_data = match_ref_data.groups()
            ref = group_data[0].strip()
        if not ref and match_ref_2_data:
            group_data = match_ref_2_data.groups()
            ref = group_data[0].strip()
        if match_data:
            group_data = match_data.groups()
            name = group_data[0]
            name = re.sub(r'{}\s*.\s*'.format(Const.PAYPAL_PREFIX), '', name)
            name = name.replace(Const.PAYPAL_PREFIX, '')
            name = re.sub(r'^\s*.\s+', '', name)
            name = name.strip()
            description = group_data[1].capitalize().strip()
            for uname, acc in Const.UNKNOWN_PAYPALS_MAP.items():
                if uname.upper() in name.upper():
                    account = acc

        if not name and match_no_name_data:
            group_data = match_no_name_data.groups()
            name = None
            description = group_data[0].strip()
            account = Const.EXPENSE_PAYPAL_UNKNOWN_ACCOUNT

        if match_data or match_no_name_data:
            ret = {'account': account, 'amount': string_to_amount_value(row[Const.ROW_NAME_VALUE]),
                   'payee': row[Const.ROW_NAME_RECIPIENT].strip()}
            # if not row[ROW_NAME_RECIPIENT].strip().startswith(PAYEE_PAYPAL):
            #  ret['payee'] = row[ROW_NAME_RECIPIENT].strip()
            if name:
                ret['name'] = name
            if description:
                ret['description'] = description
            if ref:
                ret['ref'] = ref
            if not row[Const.ROW_NAME_RECIPIENT].strip().startswith(Const.PAYEE_PAYPAL):
                ret['payee'] = row[Const.ROW_NAME_RECIPIENT].strip()
            if row[Const.ROW_NAME_CURRENCY] != Const.CURRENCY:
                ret['currency'] = row[Const.ROW_NAME_CURRENCY]
    return ret


def gen_paypal_rules_template(config, csv_filename, filename_yaml, year, month):
    data = []
    count = 0
    with open(csv_filename, 'r', newline='') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=Const.CSV_DELIMITER, quotechar=Const.CSV_QUOTECHAR)
        for row in reader:
            if ".{:02}.{:02}".format(month, year - 2000) in row[Const.ROW_NAME_BOOKINGDATE] and (
                    Const.PAYPAL_PREFIX in row[Const.ROW_NAME_USE] or Const.ALT_PAYPAL_SUFFIX in row[
                Const.ROW_NAME_REFERENCE] or Const.ALT_PAYPAL_SUFFIX in row[
                        Const.ROW_NAME_RECIPIENT] or Const.PAYPAL_SUFFIX in row[Const.ROW_NAME_RECIPIENT]):
                skip = False
                for ignore in Const.IGNORE_PAYPALS:
                    if re.search(ignore, row[Const.ROW_NAME_USE]) or re.search(ignore.upper(),
                                                                               row[Const.ROW_NAME_USE].upper()):
                        skip = True
                if not skip:
                    dat = gen_paypal_rule_template(row)
                    if dat:
                        data.append(dat)
            count = count + 1
    data.sort(key=sort_rule_element)
    if data:
        utils.print_succ("paypal rules find {} in {} rows for {:04}-{:02}".format(len(data), count, year, month))
        with open(filename_yaml, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)
    else:
        utils.print_succ("paypal: No entries found for {:04}-{:02}".format(year, month))
    return data
