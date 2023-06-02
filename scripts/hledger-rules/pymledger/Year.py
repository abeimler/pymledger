import datetime
import os

from pymledger import Const, utils, HledgerTemplates as Templates
from pymledger.HledgerBudget import gen_budget_rules, gen_budget_rules_from_data, gen_forecast_rules, \
    gen_forecast_rules_from_data, sort_budget_element, gen_budget_entry_empty, gen_budget_rules_from_data_yearly
from pymledger.HledgerOpening import get_opening_from_yml_file
from pymledger.HledgerUtils import amount_to_journal_amount_string, get_close_year_balance, get_open_year_balance
from pymledger.Month import gen_month


def gen_year(config, year):
    now = datetime.datetime.now()
    src_year_dir = os.path.join(Const.SOURCE_PATH, "{}".format(year))
    year_dir = os.path.join(Const.JOURNALS_PATH, "{}".format(year))

    if not os.path.exists(year_dir):
        os.mkdir(year_dir)

    budget_filename = os.path.join(year_dir, "{:04}.budget.hledger".format(year))
    forecast_filename = os.path.join(year_dir, "{:04}.forecast.hledger".format(year))
    year_filename = os.path.join(year_dir, "{:04}.hledger".format(year))
    open_year_filename = os.path.join(year_dir, "open.{:04}.hledger".format(year))
    closed_year_filename = os.path.join(year_dir, "closed.{:04}.hledger".format(year))

    last_year = year - 1
    last_year_dir = os.path.join(Const.JOURNALS_PATH, "{}".format(last_year))
    open_last_year_filename = os.path.join(last_year_dir, "open.{:04}.hledger".format(last_year))

    first_src_month_dir = os.path.join(src_year_dir, "{:04}-{:02}".format(year, 1))
    first_month_opening_yaml_filename = os.path.join(first_src_month_dir, "{:04}-{:02}.opening.yaml".format(year, 1))

    opening_yaml_filename = os.path.join(src_year_dir, "{:04}.opening.yaml".format(year))

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
                default_accounts = default_accounts + Templates.DEFINE_ACCOUNT_ENTRY_FORMAT.format(account=account_name)
                skip_accounts.add(account_name)
        default_accounts = default_accounts + '\n'

    sub_accounts = ''
    for account in Const.ACCOUNTS:
        if account not in skip_accounts:
            sub_accounts = sub_accounts + Templates.DEFINE_ACCOUNT_ENTRY_FORMAT.format(account=account)

    budget_data = []
    if 'monthly' in config and 'budget' in config['monthly']:
        for budget in config['monthly']['budget']:
            dat = {'account': budget.get('account', '').strip(), 'amount': budget.get('amount', 0.0),
                   'currency': budget.get('currency', Const.CURRENCY)}
            if budget.get('comment'):
                dat['comment'] = budget.get('comment')
            budget_data.append(dat)
    if 'yearly' in config and 'budget' in config['yearly']:
        for budget in config['yearly']['budget']:
            dat = {'account': budget.get('account', '').strip(), 'amount': budget.get('amount', 0.0), 'yearly': True,
                   'currency': budget.get('currency', Const.CURRENCY)}
            if budget.get('comment'):
                dat['comment'] = budget.get('comment')
            budget_data.append(dat)

    with open(forecast_filename, 'w') as file:
        budget_accounts = ''
        for entry in budget_data:
            if 'account' in entry:
                if 'yearly' in entry and entry['yearly']:
                    amount = entry.get('amount', 0.0)
                    account_name = entry['account'].strip()
                    expense_account = ''
                    if account_name in Const.FORECAST_BUDGET_EXPENSE_MAP:
                        expense_account = Templates.FORECAST_ACCOUNT_FORMAT.format(
                            Const.FORECAST_BUDGET_EXPENSE_MAP[account_name])
                    elif Const.BUDGET_ACCOUNT in account_name:
                        expense_account = "{}:{}".format(Const.EXPENSES_ACCOUNT,
                                                         account_name.replace(Const.BUDGET_ACCOUNT, ''))
                    if expense_account:
                        budget_accounts = budget_accounts + Templates.FORECAST_ENTRY_FORMAT.format(
                            account=expense_account.strip(), amount=amount_to_journal_amount_string(amount),
                            currency=entry.get('currency', Const.CURRENCY))
            else:
                utils.print_error("no account in budget")
        includes = ''
        for month in range(1, 13):
            includes = includes + "include {0:04}-{1:02}/{0:04}-{1:02}.forecast.hledger\n".format(year, month)
        file.write(
            Templates.YEAR_FORECAST_CONTENT_TEMPLATE.substitute(account=Const.SALERY_ACCOUNT, date="{:04}".format(year),
                                                                year="${:04}".format(year),
                                                                accounts=budget_accounts.rstrip('\n'),
                                                                checking=Const.CHECKING_ACCOUNT, includes=includes))

    with open(year_filename, 'w') as journal_file:
        includes = ''
        for month in range(1, 13):
            includes = includes + "include {0:04}-{1:02}/{0:04}-{1:02}.hledger\n".format(year, month)
        journal_file.write(
            Templates.YEAR_CONTENT_TEMPLATE.substitute(now=now.strftime('%Y-%m-%d %H:%M:%S'), year="{:04}".format(year),
                                                       default_accounts=default_accounts, sub_accounts=sub_accounts,
                                                       currency=Const.CURRENCY, commodity=Const.COMMODITY,
                                                       decimal_mark=Const.DECIMAL_MARK, includes=includes))

    if Const.GEN_OPENINGS or Const.GEN_CLOSINGS_AND_OPENINGS:
        opening_year = ';;; no opening'
        if os.path.exists(first_month_opening_yaml_filename):
            opening_year = get_opening_from_yml_file(year, 1, first_month_opening_yaml_filename, '', True)
        elif os.path.exists(opening_yaml_filename):
            opening_year = get_opening_from_yml_file(year, month, opening_yaml_filename)
        elif os.path.exists(open_last_year_filename):
            utils.print_verbose("read open last years journal, {:04}: {}".format(year, open_last_year_filename))
            opening_year = get_open_year_balance(last_year, open_last_year_filename)
        else:
            utils.print_warn("no file for opening, {:04}: '{}' or '{}'".format(year, opening_yaml_filename,
                                                                               first_month_opening_yaml_filename))

        with open(open_year_filename, 'w') as open_year_file:
            includes = ''
            for month in range(1, 13):
                includes = includes + "include {0:04}-{1:02}/{0:04}-{1:02}.hledger\n".format(year, month)
            open_year_file.write(Templates.OPEN_YEAR_CONTENT_TEMPLATE.substitute(now=now.strftime('%Y-%m-%d %H:%M:%S'),
                                                                                 year="{:04}".format(year),
                                                                                 default_accounts=default_accounts,
                                                                                 sub_accounts=sub_accounts,
                                                                                 currency=Const.CURRENCY,
                                                                                 commodity=Const.COMMODITY,
                                                                                 decimal_mark=Const.DECIMAL_MARK,
                                                                                 includes=includes,
                                                                                 opening=opening_year))
            utils.print_succ("write year open journal, {:04}: {}".format(year, open_year_filename))

        if Const.GEN_CLOSINGS_AND_OPENINGS:
            closing_year = ';;; no closing'
            if os.path.exists(open_year_filename):
                utils.print_verbose("read open years journal, {:04}: {}".format(year, open_year_filename))
                closing_year = get_close_year_balance(year, open_year_filename)
            else:
                utils.print_warn("no file for closing, {:04}-{:02}: '{}'".format(year, month, open_year_filename))
            with open(closed_year_filename, 'w') as closed_year_file:
                closed_year_file.write(
                    Templates.CLOSED_YEAR_CONTENT_TEMPLATE.substitute(now=now.strftime('%Y-%m-%d %H:%M:%S'),
                                                                      year="{:04}".format(year),
                                                                      default_accounts=default_accounts,
                                                                      sub_accounts=sub_accounts,
                                                                      currency=Const.CURRENCY,
                                                                      commodity=Const.COMMODITY,
                                                                      decimal_mark=Const.DECIMAL_MARK,
                                                                      includes=includes, opening=opening_year,
                                                                      closing=closing_year))
                utils.print_succ("write yearly closed journal, {:04}: {}".format(year, closed_year_filename))

    for month in range(1, 13):
        gen_source_files = Const.GEN_ALL_MONTHS or (year == now.year and month <= now.month)
        gen_month(config, year, month, none_gen_source_files=not gen_source_files)

    gen_budget_rules_from_data_yearly(config, year, budget_data, budget_filename)
