import yaml
import os

from pymledger import Const, HledgerTemplates as Templates, utils
from pymledger.HledgerUtils import amount_to_journal_amount_string


def sort_budget_element(elem):
    return elem['account']


def gen_budget_rules_last_month_from_data(year, month, data, budget_filename):
    last_year = year
    last_month = month - 1
    if month == 1:
        last_year = year - 1
        last_month = 12
    ret = set()
    with open(budget_filename, 'w') as file:
        accounts = ''
        data.sort(key=sort_budget_element)
        for entry in data:
            if 'account' in entry:
                account_name = entry['account'].strip()
                account = Templates.BUDGET_ACCOUNT_FORMAT.format(account_name)
                if 'comment' in entry:
                    entry = Templates.BUDGET_ENTRY_WITH_COMMENT_FORMAT.format(account=account.strip(),
                                                                              amount=amount_to_journal_amount_string(
                                                                                  entry.get('amount', 0.0)),
                                                                              currency=entry.get('currency',
                                                                                                 Const.CURRENCY),
                                                                              comment=entry.get('comment').strip())
                else:
                    entry = Templates.BUDGET_ENTRY_FORMAT.format(account=account.strip(),
                                                                 amount=amount_to_journal_amount_string(
                                                                     entry.get('amount', 0.0)),
                                                                 currency=entry.get('currency',
                                                                                    Const.CURRENCY))
                accounts = accounts + entry
                ret.add(account_name)
            else:
                utils.print_error("no account in budget")
        file.write(Templates.BUDGET_CONTENT_TEMPLATE.substitute(account=Const.SALERY_ACCOUNT,
                                                                date="{:04}/{:02}".format(last_year, last_month),
                                                                year="${:04}".format(year), month="{:02}".format(month),
                                                                accounts=accounts))
    return ret


def gen_budget_entry_from_data(year, month, day, data, budget_filename):
    ret = set()
    with open(budget_filename, 'w') as file:
        accounts = ''
        data.sort(key=sort_budget_element)
        for entry in data:
            if 'account' in entry:
                account_name = entry['account'].strip()
                account = Templates.BUDGET_ACCOUNT_FORMAT.format(account_name)
                if 'comment' in entry:
                    entry = Templates.BUDGET_ENTRY_WITH_COMMENT_FORMAT.format(account=account.strip(),
                                                                              amount=amount_to_journal_amount_string(
                                                                                  entry.get('amount', 0.0)),
                                                                              currency=entry.get('currency',
                                                                                                 Const.CURRENCY),
                                                                              comment=entry.get('comment').strip())
                else:
                    entry = Templates.BUDGET_ENTRY_FORMAT.format(account=account.strip(),
                                                                 amount=amount_to_journal_amount_string(
                                                                     entry.get('amount', 0.0)),
                                                                 currency=entry.get('currency',
                                                                                    Const.CURRENCY))
                accounts = accounts + entry
                ret.add(account_name)
            else:
                utils.print_error("no account in budget")
        file.write(Templates.CURRENT_MONTH_BUDGET_CONTENT_TEMPLATE.substitute(account=Const.CHECKING_ACCOUNT,
                                                                              date="{:04}/{:02}/{:02}".format(year,
                                                                                                              month,
                                                                                                              day),
                                                                              year="${:04}".format(year),
                                                                              month="{:02}".format(month),
                                                                              day="{:02}".format(day),
                                                                              accounts=accounts.rstrip()))
    return ret


def gen_budget_entry_empty(year, month, day, data, budget_filename):
    ret = set()
    with open(budget_filename, 'w') as file:
        data.sort(key=sort_budget_element)
        file.write(Templates.CURRENT_MONTH_BUDGET_CONTENT_EMPTY_TEMPLATE.substitute(
            date="{:04}/{:02}/{:02}".format(year, month, day), year="${:04}".format(year), month="{:02}".format(month), day="{:02}".format(day)))
    return ret


def gen_budget_rules_from_data(config, year, month, data, budget_filename):
    if 'monthly' in config and 'use_last_income_for_budget' in config['monthly'] and config['monthly'][
        'use_last_income_for_budget']:
        return gen_budget_rules_last_month_from_data(year, month, data, budget_filename)
    day = config['monthly']['budget_day'] if 'monthly' in config and 'use_last_income_for_budget' in config[
        'monthly'] and config['monthly']['budget_day'] else 1
    return gen_budget_entry_from_data(year, month, day, data, budget_filename)


def gen_budget_rules_from_data_yearly(config, year, budget_data, budget_filename):
    if 'yearly' in config and 'use_last_income_for_budget' in config['yearly'] and config['yearly']['use_last_income_for_budget']:
        with open(budget_filename, 'w') as file:
            budget_accounts = ''
            for entry in budget_data:
                if 'account' in entry:
                    if 'yearly' in entry and entry['yearly']:
                        amount = round(entry.get('amount', 0.0) / 12, 2)
                        account_name = entry['account'].strip()
                        account = Templates.BUDGET_ACCOUNT_FORMAT.format(account_name)
                        if 'comment' in entry:
                            budget_accounts = budget_accounts + Templates.BUDGET_ENTRY_WITH_COMMENT_FORMAT.format(account=account.strip(),
                                                                                                amount=amount_to_journal_amount_string(
                                                                                                    amount),
                                                                                                currency=entry.get(
                                                                                                    'currency',
                                                                                                    Const.CURRENCY),
                                                                                                comment=entry.get('comment'))
                        else:
                            budget_accounts = budget_accounts + Templates.BUDGET_ENTRY_FORMAT.format(account=account.strip(),
                                                                                                amount=amount_to_journal_amount_string(
                                                                                                    amount),
                                                                                                currency=entry.get(
                                                                                                    'currency',
                                                                                                    Const.CURRENCY))
                else:
                    utils.print_error("no account in budget")
            file.write(
                    Templates.YEAR_BUDGET_CONTENT_TEMPLATE.substitute(account=Const.SALERY_ACCOUNT, date="{:04}".format(year),
                                                                year="${:04}".format(year), accounts=budget_accounts.rstrip()))
    else:
        with open(budget_filename, 'w') as file:
            entires=''
            for month in range(1, 13):
                src_year_dir = os.path.join(Const.SOURCE_PATH, "{}".format(year))
                src_month_dir = os.path.join(src_year_dir, "{:04}-{:02}".format(year, month))
                src_month_csv_dir = os.path.join(src_month_dir, 'csv')
                csv_filename = os.path.join(src_month_csv_dir, "{:04}-{:02}.bank.csv".format(year, month))
                bank_entires_empty = not os.path.exists(csv_filename) or os.stat(csv_filename).st_size == 0
                if not bank_entires_empty:
                    budget_accounts = ''
                    for entry in budget_data:
                        if 'account' in entry:
                            if 'yearly' in entry and entry['yearly']:
                                amount = round(entry.get('amount', 0.0) / 12, 2)
                                account_name = entry['account'].strip()
                                account = Templates.BUDGET_ACCOUNT_FORMAT.format(account_name)
                                if 'comment' in entry:
                                    budget_accounts = budget_accounts + Templates.BUDGET_ENTRY_WITH_COMMENT_FORMAT.format(account=account.strip(),
                                                                                                        amount=amount_to_journal_amount_string(
                                                                                                            amount),
                                                                                                        currency=entry.get(
                                                                                                            'currency',
                                                                                                            Const.CURRENCY),
                                                                                                        comment=entry.get('comment'))
                                else:
                                    budget_accounts = budget_accounts + Templates.BUDGET_ENTRY_FORMAT.format(account=account.strip(),
                                                                                                        amount=amount_to_journal_amount_string(
                                                                                                            amount),
                                                                                                        currency=entry.get(
                                                                                                            'currency',
                                                                                                            Const.CURRENCY))
                        else:
                            utils.print_error("no account in budget")
                    day = config['monthly']['budget_day'] if 'monthly' in config and 'use_last_income_for_budget' in config[
                    'monthly'] and config['monthly']['budget_day'] else 1
                    entires = entires + Templates.CURRENT_YEAR_BUDGET_CONTENT_ENTRY_TEMPLATE.substitute(date="{:04}-{:02}-{:02}".format(year, month, day),
                                                                year="{:04}".format(year), month="{:02}".format(month), day="{:02}".format(day), 
                                                                accounts=budget_accounts.rstrip(),
                                                                account=Const.CHECKING_ACCOUNT).rstrip() + '\n'
            file.write(
                    Templates.CURRENT_YEAR_BUDGET_CONTENT_TEMPLATE.substitute(date="{:04}".format(year),
                                                                year="${:04}".format(year), entires=entires))


def gen_budget_rules(config, year, month, budget_yaml_filename, budget_filename):
    with open(budget_yaml_filename) as data_file:
        data = yaml.load(data_file, Loader=yaml.FullLoader)
        return gen_budget_rules_from_data(config, year, month, data, budget_filename)


def gen_forecast_rules_from_data(config, year, month, data, forecast_filename):
    ret = set()
    with open(forecast_filename, 'w') as file:
        accounts = ''
        data.sort(key=sort_budget_element)
        for entry in data:
            if 'account' in entry:
                account_name = entry['account'].strip()
                expense_account = ''
                if account_name in Const.FORECAST_BUDGET_EXPENSE_MAP:
                    expense_account = Templates.FORECAST_ACCOUNT_FORMAT.format(
                        Const.FORECAST_BUDGET_EXPENSE_MAP[account_name])
                elif Const.BUDGET_ACCOUNT in account_name:
                    expense_account = "{}:{}".format(Const.EXPENSES_ACCOUNT,
                                                     account_name.replace(Const.BUDGET_ACCOUNT, ''))
                if expense_account:
                    if 'comment' in entry:
                        accounts = accounts + Templates.FORECAST_ENTRY_WITH_COMMENT_FORMAT.format(account=expense_account.strip(),
                                                                                 amount=amount_to_journal_amount_string(
                                                                                     entry.get('amount', 0.0)),
                                                                                 currency=entry.get('currency',
                                                                                                    Const.CURRENCY), comment=entry.get('comment'))
                    else:
                        accounts = accounts + Templates.FORECAST_ENTRY_FORMAT.format(account=expense_account.strip(),
                                                                                    amount=amount_to_journal_amount_string(
                                                                                        entry.get('amount', 0.0)),
                                                                                    currency=entry.get('currency',
                                                                                                        Const.CURRENCY))
                    ret.add(expense_account)
            else:
                utils.print_error("no account in budget")
        if 'monthly' in config and 'forecast_income' in config['monthly']:
            accounts = accounts + Templates.FORECAST_ENTRY_FORMAT.format(account=Const.SALERY_ACCOUNT.strip(),
                                                                         amount=amount_to_journal_amount_string(
                                                                             -config['monthly']['forecast_income']),
                                                                         currency=Const.CURRENCY)
        file.write(
            Templates.FORECAST_CONTENT_TEMPLATE.substitute(account=Const.SALERY_ACCOUNT,
                                                           date="{:04}/{:02}".format(year, month),
                                                           year="{:04}".format(year), month="{:02}".format(month),
                                                           accounts=accounts.rstrip('\n'),
                                                           checking=Const.CHECKING_ACCOUNT))
    return ret


def gen_forecast_rules(config, year, month, budget_yaml_filename, forecast_filename):
    with open(budget_yaml_filename) as data_file:
        data = yaml.load(data_file, Loader=yaml.FullLoader)
        return gen_forecast_rules_from_data(config, year, month, data, forecast_filename)
