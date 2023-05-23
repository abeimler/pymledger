import datetime
import os
import shutil

import yaml

from pymledger import Const, utils, HledgerTemplates as Templates
from pymledger.HledgerAmazonRules import gen_amazon_rules, gen_amazon_rules_template
from pymledger.HledgerBudget import gen_budget_rules, gen_budget_rules_from_data, gen_forecast_rules, \
    gen_forecast_rules_from_data, sort_budget_element, gen_budget_entry_empty
from pymledger.HledgerOpening import get_opening_from_yml_file
from pymledger.HledgerPayPalRules import gen_paypal_rules, gen_paypal_rules_template
from pymledger.HledgerRules import gen_common_rules
from pymledger.HledgerUtils import amount_to_journal_amount_string, get_close_month_balance, get_open_month_balance


def gen_month(config, year, month, none_gen_source_files=False):
    now = datetime.datetime.now()

    src_year_dir = os.path.join(Const.SOURCE_PATH, "{}".format(year))
    src_month_dir = os.path.join(src_year_dir, "{:04}-{:02}".format(year, month))
    src_month_csv_dir = os.path.join(src_month_dir, 'csv')

    year_dir = os.path.join(Const.JOURNALS_PATH, "{}".format(year))
    month_dir = os.path.join(year_dir, "{:04}-{:02}".format(year, month))
    rules_month_dir = os.path.join(month_dir, 'rules')

    last_year = year
    last_month = month - 1
    last_year_dir = os.path.join(Const.JOURNALS_PATH, "{}".format(last_year))
    last_month_dir = os.path.join(year_dir, "{:04}-{:02}".format(year, last_month))
    if month == 1:
        last_year = year - 1
        last_month = 12
        last_year_dir = os.path.join(Const.JOURNALS_PATH, "{}".format(last_year))
        last_month_dir = os.path.join(last_year_dir, "{:04}-{:02}".format(year, last_month))

    if none_gen_source_files:
        utils.print_verbose("skip generate source files for {:04}-{:02}".format(year, month))

    if not none_gen_source_files:
        if not os.path.exists(Const.SOURCE_PATH):
            os.mkdir(Const.SOURCE_PATH)
        if not os.path.exists(src_year_dir):
            os.mkdir(src_year_dir)
        if not os.path.exists(src_month_dir):
            os.mkdir(src_month_dir)
        if not os.path.exists(src_month_csv_dir):
            os.mkdir(src_month_csv_dir)

    if not os.path.exists(year_dir):
        os.mkdir(year_dir)
    if not os.path.exists(month_dir):
        os.mkdir(month_dir)
    if not os.path.exists(rules_month_dir):
        os.mkdir(rules_month_dir)

    src_custom_filename = os.path.join(src_month_dir, "{:04}-{:02}.custom.hledger".format(year, month))
    amazon_yaml_filename = os.path.join(src_month_dir, "{:04}-{:02}.amazon.yaml".format(year, month))
    paypal_yaml_filename = os.path.join(src_month_dir, "{:04}-{:02}.paypal.yaml".format(year, month))
    budget_yaml_filename = os.path.join(src_month_dir, "{:04}-{:02}.budget.yaml".format(year, month))
    cash_yaml_filename = os.path.join(src_month_dir, "{:04}-{:02}.cash.yaml".format(year, month))
    opening_yaml_filename = os.path.join(src_month_dir, "{:04}-{:02}.opening.yaml".format(year, month))
    reconcile_yaml_filename = os.path.join(src_month_dir, "{:04}-{:02}.reconcile.yaml".format(year, month))

    template_budget_yaml_filename = os.path.join(src_month_dir, "template.{:04}-{:02}.budget.yaml".format(year, month))
    template_amazon_yaml_filename = os.path.join(src_month_dir, "template.{:04}-{:02}.amazon.yaml".format(year, month))
    template_paypal_yaml_filename = os.path.join(src_month_dir, "template.{:04}-{:02}.paypal.yaml".format(year, month))
    month_yaml_filename = os.path.join(src_month_dir, "{:04}-{:02}.yaml".format(year, month))

    csv_filename = os.path.join(src_month_csv_dir, "{:04}-{:02}.bank.csv".format(year, month))

    custom_filename = os.path.join(month_dir, "{:04}-{:02}.custom.hledger".format(year, month))
    cash_filename = os.path.join(month_dir, "{:04}-{:02}.cash.hledger".format(year, month))
    bank_filename = os.path.join(month_dir, "{:04}-{:02}.bank.hledger".format(year, month))
    budget_filename = os.path.join(month_dir, "{:04}-{:02}.budget.hledger".format(year, month))
    forecast_filename = os.path.join(month_dir, "{:04}-{:02}.forecast.hledger".format(year, month))
    month_filename = os.path.join(month_dir, "{:04}-{:02}.hledger".format(year, month))
    reconcile_filename = os.path.join(month_dir, "{:04}-{:02}.reconcile.hledger".format(year, month))

    open_month_filename = os.path.join(month_dir, "open.{:04}-{:02}.hledger".format(year, month))
    closed_month_filename = os.path.join(month_dir, "closed.{:04}-{:02}.hledger".format(year, month))
    last_open_month_filename = os.path.join(last_month_dir, "open.{:04}-{:02}.hledger".format(last_year, last_month))
    last_closed_month_filename = os.path.join(last_month_dir,
                                              "closed.{:04}-{:02}.hledger".format(last_year, last_month))

    csv_rules_filename = os.path.join(rules_month_dir, "{:04}-{:02}.bank.csv.rules".format(year, month))
    amazon_csv_rules_filename = os.path.join(rules_month_dir, "{:04}-{:02}.bank.amazon.csv.rules".format(year, month))
    paypal_csv_rules_filename = os.path.join(rules_month_dir, "{:04}-{:02}.bank.paypal.csv.rules".format(year, month))

    month_accounts = set()

    bank_entires_empty = not os.path.exists(csv_filename) or os.stat(csv_filename).st_size == 0

    if not none_gen_source_files:
        if not os.path.exists(csv_filename):
            with open(csv_filename, 'w') as csv_file:
                pass
            utils.print_verbose("touch csv: {}".format(csv_filename))

        amazon_rules = gen_amazon_rules_template(csv_filename, template_amazon_yaml_filename, year, month)
        utils.print_succ("generate Amazon rules: {}".format(template_amazon_yaml_filename))

        paypal_rules = gen_paypal_rules_template(config, csv_filename, template_paypal_yaml_filename, year, month)
        utils.print_succ("generate PayPal rules: {}".format(template_paypal_yaml_filename))

        for amazon_rule in amazon_rules:
            month_accounts.add(amazon_rule['account'])
        for paypal_rule in paypal_rules:
            month_accounts.add(paypal_rule['account'])

    if not none_gen_source_files:
        if not os.path.exists(src_custom_filename):
            with open(src_custom_filename, 'w') as src_custom_hledger_file:
                src_custom_hledger_file.write(""";; TODO: write your custom hledger entries here""")
            utils.print_verbose("touch yml: {}".format(src_custom_filename))
    if os.path.exists(src_custom_filename):
        shutil.copy(src_custom_filename, custom_filename)
        utils.print_succ("copy custom hleder journal: {} -> {}".format(src_custom_filename, custom_filename))

    if not os.path.exists(custom_filename):
        with open(custom_filename, 'w') as custom_hledger_file:
            custom_hledger_file.write(""";; TODO: write your custom hledger entries here""")
        utils.print_succ("touch custom hleder journal: {}".format(custom_filename))

    if not none_gen_source_files:
        if not os.path.exists(cash_yaml_filename):
            with open(cash_yaml_filename, 'w') as cash_yaml_file:
                pass
            utils.print_verbose("touch yml: {}".format(cash_yaml_filename))

        if not os.path.exists(month_yaml_filename):
            with open(month_yaml_filename, 'w') as month_yaml_file:
                pass
            utils.print_verbose("touch yml: {}".format(month_yaml_filename))

        if not os.path.exists(amazon_yaml_filename):
            with open(amazon_yaml_filename, 'w') as amazon_yaml_file:
                pass
            utils.print_verbose("touch yml: {}".format(amazon_yaml_filename))

        if not os.path.exists(paypal_yaml_filename):
            with open(paypal_yaml_filename, 'w') as paypal_yaml_file:
                pass
            utils.print_verbose("touch yml: {}".format(paypal_yaml_filename))

        if not os.path.exists(template_amazon_yaml_filename):
            with open(template_amazon_yaml_filename, 'w') as template_amazon_yaml_file:
                pass
            utils.print_verbose("touch yml: {}".format(template_amazon_yaml_filename))

        if not os.path.exists(template_paypal_yaml_filename):
            with open(template_paypal_yaml_filename, 'w') as template_paypal_yaml_file:
                pass
            utils.print_verbose("touch yml: {}".format(template_paypal_yaml_filename))

    budget_data = []
    if 'monthly' in config and 'budget' in config['monthly']:
        for budget in config['monthly']['budget']:
            if 'account' in budget:
                dat = {'account': budget['account'], 'amount': budget.get('amount', 0.0)}
                if budget.get('comment'):
                    dat['comment'] = budget.get('comment')
                budget_data.append(dat)
            else:
                utils.print_error("no 'account' in budget")
    budget_data.sort(key=sort_budget_element)

    if not none_gen_source_files:
        with open(template_budget_yaml_filename, 'w') as budget_yaml_file:
            yaml.dump(budget_data, budget_yaml_file, default_flow_style=False)
            utils.print_verbose("write template monthly budget yml file, {:04}-{:02}: {}".format(year, month,
                                                                                                 template_budget_yaml_filename))
        if not os.path.exists(budget_yaml_filename):
            with open(budget_yaml_filename, 'w') as budget_yaml_file:
                yaml.dump(budget_data, budget_yaml_file, default_flow_style=False)
                utils.print_verbose(
                    "write monthly budget yml file, {:04}-{:02}: {}".format(year, month, budget_yaml_filename))

    if os.path.exists(budget_yaml_filename):
        with open(budget_yaml_filename, 'r') as budget_yaml_file:
            budget_data = yaml.safe_load(budget_yaml_file)

    cash_entires = ''
    if os.path.exists(cash_yaml_filename):
        cash_data = ''
        with open(cash_yaml_filename, 'r') as cash_yaml_file:
            cash_data = yaml.safe_load(cash_yaml_file)
            if cash_data:
                for cash in cash_data:
                    if 'account' in cash:
                        account_name = cash['account'].strip()
                        cash_entires = cash_entires + Templates.CASH_JOURNAL_ENTRY_FORMAT.format(year=year, month=month,
                                                                                                 day=int(cash.get('day',
                                                                                                                  1)),
                                                                                                 description=cash.get(
                                                                                                     'description', ''),
                                                                                                 account=account_name,
                                                                                                 amount=amount_to_journal_amount_string(
                                                                                                     cash.get('amount',
                                                                                                              0.0)),
                                                                                                 currency=cash.get(
                                                                                                     'currency',
                                                                                                     Const.CURRENCY),
                                                                                                 cash_account=Const.CASH_ACCOUNT)
                        month_accounts.add(account_name)
                    else:
                        utils.print_error(
                            "no 'account' in cash: {} {}".format(cash.get('day', ''), cash.get('description', '')))
    with open(cash_filename, 'w') as cash_file:
        cash_file.write(
            Templates.CASH_JOURNAL_CONTENT_TEMPLATE.substitute(entires=cash_entires, year="{:04}".format(year),
                                                               month="{:02}".format(month)))
    utils.print_succ("write monthly cash journal, {:04}-{:02}: {}".format(year, month, cash_filename))

    month_rules = ''
    if os.path.exists(month_yaml_filename):
        utils.print_verbose("read month yml: {}".format(month_yaml_filename))
        with open(month_yaml_filename, 'r') as month_yaml_file:
            month_rules_data = yaml.safe_load(month_yaml_file)
            if month_rules_data:
                month_rules = gen_common_rules(month_rules_data)
                for rule in month_rules_data:
                    if 'account' in rule:
                        month_accounts.add(rule['account'])
    with open(csv_rules_filename, 'w') as csv_rules_file:
        csv_rules_file.write(Templates.CSV_RULES_CONTENT_TEAMPLTE.substitute(now=now.strftime('%Y-%m-%d %H:%M:%S'),
                                                                             year="{:04}".format(year),
                                                                             month="{:02}".format(month),
                                                                             rules=month_rules))
        utils.print_succ("write monthly rules file, {:04}-{:02}: {}".format(year, month, csv_rules_filename))

    if os.path.exists(amazon_yaml_filename):
        utils.print_verbose("read amazon yml: {}".format(amazon_yaml_filename))
        amazon_accounts = gen_amazon_rules(config, amazon_yaml_filename, amazon_csv_rules_filename,
                                           "{:04}".format(year), "{:02}".format(month))
        month_accounts = month_accounts.union(amazon_accounts)
        utils.print_succ("write monthly amazon rules, {:04}-{:02}: {}".format(year, month, amazon_csv_rules_filename))
    else:
        with open(amazon_csv_rules_filename, 'w') as amazon_csv_rules_file:
            pass
        utils.print_succ("touch monthly amazon rules, {:04}-{:02}: {}".format(year, month, amazon_csv_rules_filename))

    if os.path.exists(paypal_yaml_filename):
        utils.print_verbose("read paypal yml: {}".format(paypal_yaml_filename))
        paypal_accounts = gen_paypal_rules(config, paypal_yaml_filename, paypal_csv_rules_filename,
                                           "{:04}".format(year), "{:02}".format(month))
        month_accounts = month_accounts.union(paypal_accounts)
        utils.print_succ("write monthly paypal rules, {:04}-{:02}: {}".format(year, month, paypal_csv_rules_filename))
    else:
        with open(paypal_csv_rules_filename, 'w') as paypal_csv_rules_file:
            pass
        utils.print_succ("touch monthly paypal rules, {:04}-{:02}: {}".format(year, month, paypal_csv_rules_filename))

    if not bank_entires_empty:
        if os.path.exists(budget_yaml_filename):
            utils.print_verbose("read budget yml: {}".format(budget_yaml_filename))
            budget_accounts = gen_budget_rules(config, year, month, budget_yaml_filename, budget_filename)
            month_accounts = month_accounts.union(budget_accounts)
            utils.print_succ("write monthly budget rules, {:04}-{:02}: {}".format(year, month, budget_filename))
        else:
            gen_budget_rules_from_data(config, year, month, budget_data, budget_filename)
            utils.print_succ("write monthly budget rules, {:04}-{:02}: {}".format(year, month, budget_filename))
    else:
        gen_budget_entry_empty(year, month, 1, budget_data, budget_filename)
        utils.print_succ("write monthly budget rules, {:04}-{:02}: {}".format(year, month, budget_filename))

    if os.path.exists(budget_yaml_filename):
        gen_forecast_rules(config, year, month,
                           budget_yaml_filename, forecast_filename)
        utils.print_succ("write monthly budget forecast, {:04}-{:02}: {}".format(year, month, forecast_filename))
    else:
        gen_forecast_rules_from_data(config, year, month, budget_data, forecast_filename)
        utils.print_succ("write monthly budget forecast, {:04}-{:02}: {}".format(year, month, forecast_filename))

    if os.path.exists(reconcile_yaml_filename):
        utils.print_verbose("read reconcile yml: {}".format(reconcile_yaml_filename))
        with open(reconcile_yaml_filename, 'r') as reconcile_yaml_file:
            reconcile_data = yaml.safe_load(reconcile_yaml_file)
            reconcile_entires = ''
            reconcile_accounts = set()
            reconcile_accounts.add(Const.CHECKING_ACCOUNT)
            if reconcile_data:
                for data in reconcile_data:
                    if 'amount' in data:
                        account = data.get('account', Const.CHECKING_ACCOUNT)
                        currency = data.get('currency', Const.CURRENCY)
                        description = data.get('description', Templates.RECONCILE_DEFAULT_DESCRIPTION_FORMAT)
                        amount = amount_to_journal_amount_string(data['amount'])
                        day = data.get('day', utils.last_day_of_month(year, month))
                        reconcile_entires = reconcile_entires + Templates.RECONCILE_JOURNAL_ENTRY_FORMAT.format(
                            year=year, month=month, day=day, account=account, description=description, amount=amount,
                            currency=currency, decimal_mark=Const.DECIMAL_MARK)
                        reconcile_accounts.add(account)
            reconcile_accounts = list(reconcile_accounts)
            reconcile_accounts.sort()
            accounts = ''
            for account in reconcile_accounts:
                accounts = accounts + Templates.DEFINE_ACCOUNT_ENTRY_FORMAT.format(account=account)
            with open(reconcile_filename, 'w') as reconcile_file:
                reconcile_file.write(
                    Templates.RECONCILE_CONTENT_TEMPLATE.substitute(now=now.strftime('%Y-%m-%d %H:%M:%S'),
                                                                    year="{:04}".format(year),
                                                                    month="{:02}".format(month), accounts=accounts,
                                                                    entires=reconcile_entires,
                                                                    commodity=Const.COMMODITY,
                                                                    decimal_mark=Const.DECIMAL_MARK))
            utils.print_succ("write monthly reconcile journal, {:04}-{:02}: {}".format(
                year, month, paypal_csv_rules_filename))
    else:
        with open(reconcile_filename, 'w') as reconcile_file:
            pass
        utils.print_succ("touch monthly reconcile journal, {:04}-{:02}: {}".format(year, month, reconcile_filename))

    with open(month_filename, 'w') as month_file:
        month_accounts = list(month_accounts)
        month_accounts.sort()
        accounts = ''
        for account in month_accounts:
            accounts = accounts + Templates.DEFINE_ACCOUNT_ENTRY_FORMAT.format(account=account)
        month_file.write(Templates.MONTH_CONTENT_TEMPLATE.substitute(now=now.strftime('%Y-%m-%d %H:%M:%S'),
                                                                     year="{:04}".format(year),
                                                                     month="{:02}".format(month), accounts=accounts))
        utils.print_succ("write monthly journal, {:04}-{:02}: {}".format(year, month, month_filename))

        skip_accounts = set()
        default_accounts = ''
        if 'define_accounts' in config:
            for account in config['define_accounts']:
                if 'account' in account and 'type' in account:
                    account_name = account['account'].strip()
                    type = account['type']
                    if type.upper() == 'A' or type.lower() == 'asset' or type.lower() == 'assets':
                        type = 'A'
                    elif type.upper() == 'L' or type.lower() == 'liability' or type.lower() == 'liabilities' or type.lower() == 'debts':
                        type = 'L'
                    elif type.upper() == 'E' or type.lower() == 'equity':
                        type = 'E'
                    elif type.upper() == 'R' or type.lower() == 'revenue' or type.lower() == 'revenues' or type.lower() == 'income':
                        type = 'R'
                    elif type.upper() == 'X' or type.lower() == 'expense' or type.lower() == 'expenses':
                        type = 'X'
                    elif type.upper() == 'C' or type.lower() == 'cash':
                        type = 'C'
                    default_accounts = default_accounts + Templates.DEFINE_ACCOUNT_TYPE_ENTRY_FORMAT.format(
                        account=account_name, type=type)
                    skip_accounts.add(account_name)
                elif 'account' in account:
                    account_name = account['account'].strip()
                    default_accounts = default_accounts + Templates.DEFINE_ACCOUNT_ENTRY_FORMAT.format(
                        account=account_name)
                    skip_accounts.add(account_name)
            default_accounts = default_accounts + '\n'

        sub_accounts = ''
        for account in Const.ACCOUNTS:
            if account not in skip_accounts:
                sub_accounts = sub_accounts + \
                               Templates.DEFINE_ACCOUNT_ENTRY_FORMAT.format(account=account)

        if Const.GEN_OPENINGS or Const.GEN_CLOSINGS_AND_OPENINGS:
            opening_month = ';;; no opening'
            if os.path.exists(opening_yaml_filename):
                opening_month = get_opening_from_yml_file(year, month, opening_yaml_filename, '', True)
            elif os.path.exists(last_open_month_filename):
                utils.print_verbose(
                    "read last open months journal, {:04}-{:02}: {}".format(year, month, last_open_month_filename))
                opening_month = get_open_month_balance(year, month, last_open_month_filename)
            else:
                utils.print_warn(
                    "no file for opening, {:04}-{:02}: '{}' or '{}'".format(year, month, opening_yaml_filename,
                                                                            last_closed_month_filename))

            with open(open_month_filename, 'w') as open_month_file:
                open_month_file.write(
                    Templates.OPEN_MONTH_CONTENT_TEMPLATE.substitute(now=now.strftime('%Y-%m-%d %H:%M:%S'),
                                                                     year="{:04}".format(year),
                                                                     month="{:02}".format(month), accounts=accounts,
                                                                     default_accounts=default_accounts,
                                                                     sub_accounts=sub_accounts, currency=Const.CURRENCY,
                                                                     commodity=Const.COMMODITY,
                                                                     decimal_mark=Const.DECIMAL_MARK,
                                                                     opening=opening_month))
                utils.print_succ("write monthly open journal, {:04}-{:02}: {}".format(year, month, open_month_filename))

            if Const.GEN_CLOSINGS_AND_OPENINGS:
                closing_month = ';;; no closing'
                if os.path.exists(open_month_filename):
                    utils.print_verbose(
                        "read open months journal, {:04}-{:02}: {}".format(year, month, open_month_filename))
                    closing_month = get_close_month_balance(year, month, open_month_filename)
                else:
                    utils.print_warn("no file for closing, {:04}-{:02}: '{}'".format(year, month, open_month_filename))
                with open(closed_month_filename, 'w') as closed_month_file:
                    closed_month_file.write(
                        Templates.CLOSED_MONTH_CONTENT_TEMPLATE.substitute(now=now.strftime('%Y-%m-%d %H:%M:%S'),
                                                                           year="{:04}".format(year),
                                                                           month="{:02}".format(month),
                                                                           accounts=accounts,
                                                                           default_accounts=default_accounts,
                                                                           sub_accounts=sub_accounts,
                                                                           currency=Const.CURRENCY,
                                                                           commodity=Const.COMMODITY,
                                                                           decimal_mark=Const.DECIMAL_MARK,
                                                                           opening=opening_month,
                                                                           closing=closing_month))
                    utils.print_succ(
                        "write monthly closed journal, {:04}-{:02}: {}".format(year, month, closed_month_filename))

    if os.path.exists(csv_filename) and os.path.exists(csv_rules_filename):
        cmd = [Const.HLEDGER, 'print', '-s' if Const.HLEDGER_STRICT else '', '-f', csv_filename, '--rules-file',
               csv_rules_filename,
               '-o', bank_filename]
        utils.print_info(' '.join(cmd))
        os.system(' '.join(cmd))
        utils.print_succ("write monthly bank journal, {:04}-{:02}: {}".format(year, month, bank_filename))
    else:
        with open(bank_filename, 'w') as bank_file:
            pass
        utils.print_succ("touch monthly bank journal, {:04}-{:02}: {}".format(year, month, bank_filename))
