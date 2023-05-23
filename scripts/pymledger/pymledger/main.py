"""Generate ledger rules from yaml and then generate journals from csv

Usage:
  pymledger [--hledger-path=HLEDGER] [-c config.yml] [--output-dir=OUTPUT_DIR] [--templates-dir=TEMPLATES_DIR] gen-month <year> <month> [--opening-closing | --opening] [--strict] [--verbose] 
  pymledger [--hledger-path=HLEDGER] [-c config.yml] [--output-dir=OUTPUT_DIR] [--templates-dir=TEMPLATES_DIR] gen-year <year> [--all-months] [--opening-closing | --opening] [--strict] [--verbose] 
  pymledger [--hledger-path=HLEDGER] [-c config.yml] [--output-dir=OUTPUT_DIR] [--templates-dir=TEMPLATES_DIR] gen-all [--strict] [--verbose] <years>...
  pymledger [--hledger-path=HLEDGER] [-c config.yml] [--output-dir=OUTPUT_DIR] [--templates-dir=TEMPLATES_DIR] gen-all-forecast [--verbose] <years>...
  pymledger [--hledger-path=HLEDGER] [-c config.yml] [--output-dir=OUTPUT_DIR] clean-up-csv <year> [--input-csv-delimiter=DELIMITER] [<month>] [--verbose]
  pymledger [--hledger-path=HLEDGER] [-c config.yml] [--output-dir=OUTPUT_DIR] clean-up-csv -i INPUT [-o OUTPUT] [--input-csv-delimiter=DELIMITER] [--strict] [--verbose]
  pymledger [-c config.yml] [--output-dir=OUTPUT_DIR] [--templates-dir=TEMPLATES_DIR] gen-rules [<year>] [--verbose]
  pymledger [-c config.yml] accounts [--verbose]
  pymledger [-c config.yml] beancount-options [--verbose]
  pymledger [-c config.yml] plot-senkey --source-account=ACCOUNT -i INPUT [-o OUTPUT] [--verbose]
  pymledger [-c config.yml] plot-senkey-budget -i INPUT [-o OUTPUT] [--verbose]
  pymledger [-c config.yml] plot-senkey-expenses -i INPUT [-o OUTPUT] [--verbose]
  pymledger [-c config.yml] plot-senkey-income-budget -i INPUT [-o OUTPUT] [--verbose]
  pymledger [-c config.yml] plot-senkey-budget-expenses -i INPUT [-o OUTPUT] [--verbose]
  pymledger [-c config.yml] plot-senkey-income-budget-expenses -i INPUT [-o OUTPUT] [--verbose]
  pymledger [-c config.yml] budget [--balance] [--verbose]
  pymledger [--hledger-path=HLEDGER] [--ledger2beancount-path=LEDGER2BEANCOUNT] [-c config.yml] beancount -f JOURNAL [-o OUTPUT] [--verbose]
  pymledger -h | --help
  pymledger --version


Commands:
  clean-up-csv                          clean up .csv file for input
  gen-rules                             generate hledger rules files from config
  gen-year <year>                       generate source, hledger rules and journals from csv files (input)
  gen-month <year> <month>              generate source, hledger rules and journals from csv files (input)
  accounts                              print accounts from config
  beancount-options                     print beancount options for fava
  plot-senkey                           plot Senkey-Diagram from .csv
  plot-senkey-budget                    plot Senkey-Diagram from .csv with budget
  plot-senkey-income-budget             plot Senkey-Diagram from .csv with income -> budget
  plot-senkey-expenses                  plot Senkey-Diagram from .csv with expenses
  plot-senkey-budget-expenses           plot Senkey-Diagram from .csv with budget -> expenses 
  plot-senkey-income-budget-expenses    plot Senkey-Diagram from .csv with income -> budget -> expenses
  budget                                print (montly-)buget balance

Arguments:
  --hledger-path=HLEDGER                    path to hledger execute binary [default: ./hledger]
  --ledger2beancount-path=LEDGER2BEANCOUNT  path to ledger2beancount execute binary [default: ./ledger2beancount]
  -c config.yml                             .yml config with rules and more settings [default: config.yml]
  --output-dir=OUTPUT_DIR                   output directory
  --templates-dir=TEMPLATES_DIR             templates directory from hledger- and rules-templates (amazon.csv.rules, bank.csv.rules, common.csv.rules, ...)
  --source-account=ACCOUNT                  account name for source in Senkey-Diagram
  -i INPUT                                  input .csv for clean up csv
                                            input .csv with income-,assets-budget- and expenses-accounts
  -o OUTPUT                                 output .csv for clean up csv
                                            output filename for Senkey-Diagram
                                            output filename for beancount
  -f JOURNAL                                input .journal for beancount
  --input-csv-delimiter=DELIMITER           input .csv delimiter [default: ,]

Options:
  -h, --help            show help
  -v, --version         show version
  -V, --verbose         print more details
  -s, --strict          use hledger with strict option
  --all-months          generating source files for all months
  --opening-closing     generate opening- and closing-journals
  --opening             generate only opening-journals
  --balance             only print balance from montly budget

"""
import csv
import os
import tempfile

import colorama
import yaml
from docopt import docopt

from pymledger import Const, utils, HledgerTemplates as Templates
from pymledger.HledgerCSV import clean_up_month_csv
from pymledger.HledgerOpening import get_opening_from_yml_file
from pymledger.HledgerRules import gen_rules
from pymledger.Month import gen_month
from pymledger.SankeyDiagram import get_sankey_data_budget_expenses_plotly_figure, \
    get_sankey_data_income_budget_plotly_figure, get_sankey_data_plotly_figure
from pymledger.Year import gen_year


def gen_month_cmd(config, args):
    month_str = args['<month>']
    year_str = args['<year>']

    if not year_str or not year_str.isnumeric():
        utils.print_error('year is required and must be a number')
        return

    if not month_str or not month_str.isnumeric():
        utils.print_error('month is required and must be a number')
        return

    year = int(year_str)
    month = int(month_str)

    if month < 1 or month > 12:
        utils.print_error('month must be in range 1-12')
        return

    gen_month(config, year, month)


def gen_year_cmd(config, args):
    year_str = args['<year>']

    if not year_str or not year_str.isnumeric():
        utils.print_error('year is required and must be a number')
        return 3

    year = int(year_str)

    gen_year(config, year)
    return 0


def cleanup_month_csv_cmd(config, args):
    year_str = args['<year>']
    month_str = args['<month>']

    if not year_str or not year_str.isnumeric():
        utils.print_error('year is required and must be a number')
        return

    if not month_str or not month_str.isnumeric():
        utils.print_error('month is required and must be a number')
        return 3

    year = int(year_str)
    month = int(month_str)

    clean_up_month_csv(config, year, month)
    return 0


def cleanup_year_csv_cmd(config, args):
    year_str = args['<year>']

    if not year_str or not year_str.isnumeric():
        utils.print_error('year is required and must be a number')
        return 3

    year = int(year_str)

    for month in range(1, 13):
        clean_up_month_csv(config, year, month)

    return 0


def gen_all_journal_cmd(config, args):
    years = []
    years_strs = args['<years>']
    for year_str in years_strs:
        if year_str:
            if not year_str.isnumeric():
                utils.print_error('year must be a number')
                return 3
            years.append(int(year_str))
    if len(years) == 0:
        utils.print_error('years are required')
        return 4

    start_year = years[0]
    src_start_year_dir = os.path.join(Const.SOURCE_PATH, "{}".format(start_year))
    start_year_dir = os.path.join(Const.JOURNALS_PATH, "{}".format(start_year))
    first_src_month_dir = os.path.join(
        src_start_year_dir, "{:04}-{:02}".format(start_year, 1))
    first_month_opening_yaml_filename = os.path.join(
        first_src_month_dir, "{:04}-{:02}.opening.yaml".format(start_year, 1))
    start_year_opening_yaml_filename = os.path.join(
        src_start_year_dir, "{:04}.opening.yaml".format(start_year))

    opening_yaml_filename = os.path.join(
        Const.SOURCE_PATH, "opening.yaml")

    all_filename = os.path.join(Const.JOURNALS_PATH, "all.hledger")

    title = config['title'] if 'title' in config else ''

    opening = ''
    if os.path.exists(first_month_opening_yaml_filename):
        utils.print_verbose("read first months opening for all: {}".format(first_month_opening_yaml_filename))
        opening = get_opening_from_yml_file(
            start_year, 1, first_month_opening_yaml_filename, '*', False)
    if os.path.exists(start_year_opening_yaml_filename):
        utils.print_verbose("read first years opening for all: {}".format(start_year_opening_yaml_filename))
        opening = get_opening_from_yml_file(
            start_year, 1, start_year_opening_yaml_filename, '*', False)
    elif os.path.exists(opening_yaml_filename):
        utils.print_verbose("read opening for all: {}".format(opening_yaml_filename))
        opening = get_opening_from_yml_file(start_year, 1, opening_yaml_filename, '*', False)

    includes = ''
    for year in years:
        includes = includes + "include {0:04}/{0:04}.hledger\n".format(year)

    with open(all_filename, 'w') as all_file:
        all_file.write(
            Templates.ALL_CONTENT_TEMPLATE.substitute(title=title, currency=Const.CURRENCY, commodity=Const.COMMODITY,
                                                      decimal_mark=Const.DECIMAL_MARK, includes=includes,
                                                      opening=opening, unbudget_account=Const.UNBUDGET_ACCOUNT,
                                                      start_year=start_year, checking_account=Const.CHECKING_ACCOUNT,
                                                      budget_account=Const.BUDGET_ACCOUNT,
                                                      saving_account=Const.SAVING_ACCOUNT))
        utils.print_succ("write all journal: {}".format(all_filename))

    return 0


def gen_all_forecast_cmd(config, args):
    years = []
    years_strs = args['<years>']
    for year_str in years_strs:
        if year_str:
            if not year_str.isnumeric():
                utils.print_error('year must be a number')
                return 3
            years.append(int(year_str))
    if len(years) == 0:
        utils.print_error('years are required')
        return 4

    forecast_filename = os.path.join(Const.JOURNALS_PATH, "forecast.hledger")

    includes = ''
    for year in years:
        includes = includes + "include {0:04}/{0:04}.forecast.hledger\n".format(year)

    with open(forecast_filename, 'w') as all_file:
        all_file.write(includes)
        utils.print_succ("write all forecast: {}".format(forecast_filename))

    return 0


def plot_senkey_cmd(config, args):
    source_account = args['--source-account']
    input_csv_filename = args['-i']

    if not os.path.exists(input_csv_filename):
        utils.print_error(".csv not found: {}".format(input_csv_filename))
        return 5

    with open(input_csv_filename, 'r', newline='') as csv_file:
        utils.print_verbose("read plot data rows: {}".format(input_csv_filename))
        reader = csv.DictReader(csv_file, delimiter=Const.CSV_DELIMITER, quotechar=Const.CSV_QUOTECHAR)
        rows = []
        for row in reader:
            if 'account' in row and row['account'].startswith(source_account):
                rows.append(row)

        if not rows:
            utils.print_warn("no rows found for {}".format(source_account))

        fig = get_sankey_data_plotly_figure(config, source_account, rows)
        if args['-o']:
            fig.write_image(args['-o'])
        else:
            fig.show()

    return 0


def plot_senkey_budget_cmd(config, args):
    source_account = Const.BUDGET_ACCOUNT
    input_csv_filename = args['-i']

    if not os.path.exists(input_csv_filename):
        utils.print_error(".csv not found: {}".format(input_csv_filename))
        return 5

    with open(input_csv_filename, 'r', newline='') as csv_file:
        utils.print_verbose("read plot data rows: {}".format(input_csv_filename))
        reader = csv.DictReader(csv_file, delimiter=Const.CSV_DELIMITER, quotechar=Const.CSV_QUOTECHAR)
        rows = []
        for row in reader:
            if 'account' in row and row['account'].startswith(source_account):
                rows.append(row)

        if not rows:
            utils.print_warn("no rows found for {}".format(source_account))

        fig = get_sankey_data_plotly_figure(config, source_account, rows)
        if args['-o']:
            fig.write_image(args['-o'])
        else:
            fig.show()

    return 0


def plot_senkey_expenses_cmd(config, args):
    source_account = Const.EXPENSES_ACCOUNT
    input_csv_filename = args['-i']

    if not os.path.exists(input_csv_filename):
        utils.print_error(".csv not found: {}".format(input_csv_filename))
        return

    with open(input_csv_filename, 'r', newline='') as csv_file:
        utils.print_verbose("read plot data rows: {}".format(input_csv_filename))
        reader = csv.DictReader(csv_file, delimiter=Const.CSV_DELIMITER, quotechar=Const.CSV_QUOTECHAR)
        rows = []
        for row in reader:
            if 'account' in row and row['account'].startswith(source_account):
                rows.append(row)

        if not rows:
            utils.print_warn("no rows found for {}".format(source_account))

        fig = get_sankey_data_plotly_figure(config, source_account, rows)
        if args['-o']:
            fig.write_image(args['-o'])
        else:
            fig.show()


def plot_senkey_income_budget_cmd(config, args):
    input_csv_filename = args['-i']

    if not os.path.exists(input_csv_filename):
        utils.print_error(".csv not found: {}".format(input_csv_filename))
        return 5

    with open(input_csv_filename, 'r', newline='') as csv_file:
        utils.print_verbose("read plot data rows: {}".format(input_csv_filename))
        reader = csv.DictReader(csv_file, delimiter=Const.CSV_DELIMITER, quotechar=Const.CSV_QUOTECHAR)
        income_rows = []
        for row in reader:
            if 'account' in row and row['account'].startswith(Const.INCOME_ACCOUNT):
                income_rows.append(row)

        if not income_rows:
            utils.print_warn("no rows found for {}".format(Const.INCOME_ACCOUNT))

        fig = get_sankey_data_income_budget_plotly_figure(config, Const.INCOME_ACCOUNT, income_rows,
                                                          Const.BUDGET_ACCOUNT)
        if args['-o']:
            fig.write_image(args['-o'])
        else:
            fig.show()

    return 0


def plot_senkey_budget_expenses_cmd(config, args):
    input_csv_filename = args['-i']

    if not os.path.exists(input_csv_filename):
        utils.print_error(".csv not found: {}".format(input_csv_filename))
        return 5

    with open(input_csv_filename, 'r', newline='') as csv_file:
        utils.print_verbose("read plot data rows: {}".format(input_csv_filename))
        reader = csv.DictReader(csv_file, delimiter=Const.CSV_DELIMITER, quotechar=Const.CSV_QUOTECHAR)
        budget_rows = []
        expenses_rows = []
        for row in reader:
            if 'account' in row and row['account'].startswith(Const.BUDGET_ACCOUNT):
                budget_rows.append(row)
            if 'account' in row and row['account'].startswith(Const.EXPENSES_ACCOUNT):
                expenses_rows.append(row)
        if not budget_rows:
            utils.print_warn("no rows found for {}".format(Const.BUDGET_ACCOUNT))
        if not expenses_rows:
            utils.print_warn("no rows found for {}".format(Const.EXPENSES_ACCOUNT))

        fig = get_sankey_data_budget_expenses_plotly_figure(config, Const.UNBUDGET_ACCOUNT, Const.BUDGET_ACCOUNT,
                                                            Const.EXPENSES_ACCOUNT, budget_rows, expenses_rows)
        if args['-o']:
            fig.write_image(args['-o'])
        else:
            fig.show()

    return 0


def print_budget_balance_cmd(config, args):
    print_balance = args['--balance']
    print_budget_accounts = not args['--balance']

    forecast_income = config['monthly']['forecast_income']
    budget_income = forecast_income
    budget_expenses = 0
    for budget_account, budget_data in Const.BUDGET_DATA_MAP.items():
        budget_expenses = budget_expenses + budget_data['monthly_amount']
    budget_balance = budget_income - budget_expenses

    if print_budget_accounts or print_balance:
        print(" {:<79}||{:>15} ".format('Forecast', 'monthly'))
        print("{:<80}++{:>16}".format(80 * '=', 16 * '='))

        print(" {:<79}||{:>15} ".format('Budget', ''))
        if print_budget_accounts:
            print("{:<80}++{:>16}".format(80 * '-', 16 * '-'))
            for budget_account, budget_data in Const.BUDGET_DATA_MAP.items():
                budget_value = "{:.2f} {}".format(budget_data['monthly_amount'], Const.CURRENCY)
                print(" {:<79}||{:>15} ".format(budget_account, budget_value))
        print("{:<80}++{:>16}".format(80 * '-', 16 * '-'))
        print(" {:<79}||{:>15} ".format('', "{:.2f} {}".format(budget_expenses, Const.CURRENCY)))
        print("{:<80}++{:>16}".format(80 * '=', 16 * '='))

        print(" {:<79}||{:>16}".format('Income', ''))
        if print_budget_accounts:
            print("{:<80}++{:>16}".format(80 * '-', 16 * '-'))
            print(" {:<79}||{:>15} ".format('Income (Budget)', "{:.2f} {}".format(forecast_income, Const.CURRENCY)))
        print("{:<80}++{:>16}".format(80 * '-', 16 * '-'))
        print(" {:<79}||{:>15} ".format('', "{:.2f} {}".format(budget_income, Const.CURRENCY)))

        print("{:<80}++{:>16}".format(80 * '=', 16 * '='))
        print(" {:<79}||{:>15} ".format('Net:', "{:.2f} {}".format(budget_balance, Const.CURRENCY)))

    return 0


def gen_beancount_options(config):
    ret = ''
    if 'title' in config:
        ret = ret + Templates.BEANCOUNT_OPTION_FORMAT.format(option='title', amount=config['title']) + '\n'
    ret = ret + Templates.BEANCOUNT_OPTION_FORMAT.format(option='operating_currency', amount=Const.CURRENCY) + '\n'
    ret = ret + Templates.BEANCOUNT_OPTION_FORMAT.format(option='name_assets',
                                                         amount=Const.ASSETS_ACCOUNT.capitalize()) + '\n'
    ret = ret + Templates.BEANCOUNT_OPTION_FORMAT.format(option='name_liabilities',
                                                         amount=Const.LIABILITIES_ACCOUNT.capitalize()) + '\n'
    ret = ret + Templates.BEANCOUNT_OPTION_FORMAT.format(option='name_income',
                                                         amount=Const.INCOME_ACCOUNT.capitalize()) + '\n'
    ret = ret + Templates.BEANCOUNT_OPTION_FORMAT.format(option='name_expenses',
                                                         amount=Const.EXPENSES_ACCOUNT.capitalize())
    ret = ret + Templates.BEANCOUNT_OPTION_FORMAT.format(option='operating_currency', amount=Const.CURRENCY) + '\n'
    ret = ret + Templates.BEANCOUNT_PLUGIN_FORMAT.format(plugin='beancount.plugins.auto_accounts') + '\n'
    return ret


def gen_beancount_cmd(config, args):
    input_journal_filename = args['-f']
    output_beancount_filename = args['-o']

    if not os.path.exists(input_journal_filename):
        utils.print_error(".journal not found: {}".format(input_journal_filename))
        return 6

    if not output_beancount_filename:
        output_beancount_filename = "{}.journal".format(input_journal_filename)

    print_journal_cmd = [Const.HLEDGER, '-f', input_journal_filename, '--auto', 'print']
    utils.print_info(' '.join(print_journal_cmd))
    beancount_journal = os.popen(' '.join(print_journal_cmd)).read()

    with tempfile.NamedTemporaryFile(mode='w+t', suffix='.journal') as beancount_journal_file:
        beancount_journal_file.write(beancount_journal)
        beancount_journal_file.flush()
        ledger2beancount_cmd = [Const.LEDGER2BEANCOUNT, beancount_journal_file.name]
        utils.print_debug(' '.join(ledger2beancount_cmd))
        ledger2beancount_result = os.popen(' '.join(ledger2beancount_cmd)).read()
        beancount_journal_file.close()

        with open(output_beancount_filename, 'w') as output_beancount_file:
            output_beancount_file.write(gen_beancount_options(config))
            output_beancount_file.write(ledger2beancount_result)


def init_globals(config):
    Const.IGNORE_PAYPALS = []
    Const.IGNORE_AMAZONS = []
    Const.IGNORE_PAYPALS_MAP = {}
    Const.UNKNOWN_PAYPALS = []
    Const.UNKNOWN_PAYPALS_MAP = {}
    Const.FORECAST_BUDGET_EXPENSE_MAP = {}
    Const.BUDGET_DATA_MAP = {}
    Const.ACCOUNTS_TITLE = {}

    if 'amazon' in config and 'payee' in config['amazon']:
        Const.PAYEE_AMAZON = config['amazon']['payee']
    if 'paypal' in config and 'payee' in config['paypal']:
        Const.PAYEE_PAYPAL = config['paypal']['payee']
    if 'paypal' in config and 'prefix' in config['paypal']:
        Const.PAYPAL_PREFIX = config['paypal']['prefix']
    if 'paypal' in config and 'suffix' in config['paypal']:
        Const.PAYPAL_SUFFIX = config['paypal']['suffix']
    if 'ignore_paypal' in config:
        Const.IGNORE_PAYPALS = config['ignore_paypal']
    if 'ignore_amazon' in config:
        Const.IGNORE_AMAZONS = config['ignore_amazon']

    if 'accounts' in config and 'checking' in config['accounts']:
        Const.CHECKING_ACCOUNT = config['accounts']['checking']
    if 'accounts' in config and 'paypal_unknown' in config['accounts']:
        Const.EXPENSE_PAYPAL_UNKNOWN_ACCOUNT = config['accounts']['paypal_unknown']
    if 'accounts' in config and 'amazon_unknown' in config['accounts']:
        Const.EXPENSE_AMAZON_UNKNOWN_ACCOUNT = config['accounts']['amazon_unknown']
    if 'accounts' in config and 'cash' in config['accounts']:
        Const.CASH_ACCOUNT = config['accounts']['cash']
    if 'accounts' in config and 'unknown' in config['accounts']:
        Const.EXPENSE_UNKNOWN_ACCOUNT = config['accounts']['unknown']
    if 'accounts' in config and 'salary' in config['accounts']:
        Const.SALERY_ACCOUNT = config['accounts']['salary']
    if 'accounts' in config and 'budget' in config['accounts']:
        Const.BUDGET_ACCOUNT = config['accounts']['budget']
    if 'accounts' in config and 'unbudget' in config['accounts']:
        Const.UNBUDGET_ACCOUNT = config['accounts']['unbudget']
    if 'accounts' in config and 'saving' in config['accounts']:
        Const.SAVING_ACCOUNT = config['accounts']['saving']
    if 'accounts' in config and 'assets' in config['accounts']:
        Const.ASSETS_ACCOUNT = config['accounts']['assets']
    if 'accounts' in config and 'liabilities' in config['accounts']:
        Const.LIABILITIES_ACCOUNT = config['accounts']['liabilities']
    if 'accounts' in config and 'equity' in config['accounts']:
        Const.EQUITY_ACCOUNT = config['accounts']['equity']
    if 'accounts' in config and 'opening' in config['accounts']:
        Const.OPENING_ACCOUNT = config['accounts']['opening']
        Const.CLOSING_ACCOUNT = Const.OPENING_ACCOUNT
    if 'accounts' in config and 'closing' in config['accounts']:
        Const.CLOSING_ACCOUNT = config['accounts']['closing']
    if 'accounts' in config and 'income' in config['accounts']:
        Const.INCOME_ACCOUNT = config['accounts']['income']
    if 'accounts' in config and 'expenses' in config['accounts']:
        Const.EXPENSES_ACCOUNT = config['accounts']['expenses']

    if 'amazon_rules' in config:
        for amazon_rule in config['amazon_rules']:
            if 'if' in amazon_rule:
                ifs = amazon_rule['if']
                if not isinstance(ifs, list) or isinstance(ifs, str):
                    ifs = [amazon_rule['if']]
                Const.IGNORE_AMAZONS.extend(ifs)
    if 'paypal_rules' in config:
        for paypal_rule in config['paypal_rules']:
            if not paypal_rule['account'].startswith(Const.EXPENSE_UNKNOWN_ACCOUNT) and not paypal_rule[
                'account'].startswith(Const.EXPENSE_PAYPAL_UNKNOWN_ACCOUNT):
                if 'if' in paypal_rule:
                    ifs = paypal_rule['if']
                    if not isinstance(ifs, list) or isinstance(ifs, str):
                        ifs = [paypal_rule['if']]
                    Const.IGNORE_PAYPALS.extend(ifs)
                if 'name' in paypal_rule:
                    if isinstance(paypal_rule['name'], list):
                        Const.IGNORE_PAYPALS.extend(paypal_rule['name'])
                        for name in paypal_rule['name']:
                            Const.IGNORE_PAYPALS_MAP[name] = paypal_rule['account']
                    else:
                        if paypal_rule['name']:
                            Const.IGNORE_PAYPALS.append(paypal_rule['name'])
                            Const.IGNORE_PAYPALS_MAP[paypal_rule['name']] = paypal_rule['account']
            else:
                if 'name' in paypal_rule:
                    if isinstance(paypal_rule['name'], list):
                        Const.UNKNOWN_PAYPALS.extend(paypal_rule['name'])
                        for name in paypal_rule['name']:
                            Const.UNKNOWN_PAYPALS_MAP[name] = paypal_rule['account']
                    else:
                        if paypal_rule['name']:
                            Const.UNKNOWN_PAYPALS.append(paypal_rule['name'])
                            Const.UNKNOWN_PAYPALS_MAP[paypal_rule['name']] = paypal_rule['account']

    Const.BUDGET_DATA_MAP = {}
    if 'monthly' in config and 'budget' in config['monthly']:
        for budget in config['monthly']['budget']:
            if 'account' in budget:
                account_name = budget['account'].strip()
                if account_name in Const.BUDGET_DATA_MAP:
                    Const.BUDGET_DATA_MAP[account_name]['amount'] = Const.BUDGET_DATA_MAP[account_name][
                                                                        'amount'] + budget.get('amount', 0.0)
                    Const.BUDGET_DATA_MAP[account_name]['monthly_amount'] = Const.BUDGET_DATA_MAP[account_name][
                                                                                'monthly_amount'] + budget.get('amount',
                                                                                                               0.0)
                    Const.BUDGET_DATA_MAP[account_name]['yearly_amount'] = Const.BUDGET_DATA_MAP[account_name][
                                                                               'yearly_amount'] + budget.get('amount',
                                                                                                             0.0) * 12
                else:
                    Const.BUDGET_DATA_MAP[account_name] = {'account': account_name, 'amount': budget.get('amount', 0.0),
                                                           'monthly_amount': budget.get('amount', 0.0),
                                                           'yearly_amount': budget.get('amount', 0.0) * 12,
                                                           'currency': budget.get('currency', Const.CURRENCY)}
    if 'yearly' in config and 'budget' in config['yearly']:
        for budget in config['yearly']['budget']:
            if 'account' in budget:
                account_name = budget['account'].strip()
                if account_name in Const.BUDGET_DATA_MAP:
                    Const.BUDGET_DATA_MAP[account_name]['amount'] = Const.BUDGET_DATA_MAP[account_name][
                                                                        'amount'] + budget.get('amount', 0.0)
                    Const.BUDGET_DATA_MAP[account_name]['yearly_amount'] = Const.BUDGET_DATA_MAP[account_name][
                                                                               'yearly_amount'] + budget.get('amount',
                                                                                                             0.0)
                    Const.BUDGET_DATA_MAP[account_name]['monthly_amount'] = Const.BUDGET_DATA_MAP[account_name][
                                                                                'monthly_amount'] + budget.get('amount',
                                                                                                               0.0) / 12
                else:
                    Const.BUDGET_DATA_MAP[budget['account'].strip()] = {'account': account_name,
                                                                        'amount': budget.get('amount', 0.0),
                                                                        'monthly_amount': budget.get('amount',
                                                                                                     0.0) / 12,
                                                                        'yearly_amount': budget.get('amount', 0.0),
                                                                        'yearly': True,
                                                                        'currency': budget.get('currency',
                                                                                               Const.CURRENCY)}

    budget_expense_asset_map = {}
    if 'transactions' in config:
        for transaction in config['transactions']:
            if 'expense' in transaction and 'asset' in transaction:
                if transaction['asset'] in Const.BUDGET_DATA_MAP:
                    if not transaction['asset'] in budget_expense_asset_map:
                        budget_expense_asset_map[transaction['asset']] = []
                    budget_expense_asset_map[transaction['asset']].append(transaction['expense'])

    Const.FORECAST_BUDGET_EXPENSE_MAP = {}
    for budget_account, budget_data in Const.BUDGET_DATA_MAP.items():
        if Const.BUDGET_ACCOUNT in budget_account:
            Const.FORECAST_BUDGET_EXPENSE_MAP[budget_account] = "{}:{}".format(Const.EXPENSES_ACCOUNT,
                                                                               budget_account.replace(
                                                                                   "{}:".format(Const.BUDGET_ACCOUNT),
                                                                                   '') or Const.BUDGET_ACCOUNT.replace(
                                                                                   "{}:".format(Const.ASSETS_ACCOUNT),
                                                                                   ''))
        elif Const.SAVING_ACCOUNT in budget_account:
            Const.FORECAST_BUDGET_EXPENSE_MAP[budget_account] = "{}:{}".format(Const.EXPENSES_ACCOUNT,
                                                                               budget_account.replace("{}:".format(
                                                                                   Const.SAVING_ACCOUNT), '').replace(
                                                                                   "{}:".format(Const.ASSETS_ACCOUNT),
                                                                                   '') or Const.SAVING_ACCOUNT.replace(
                                                                                   "{}:".format(Const.ASSETS_ACCOUNT),
                                                                                   ''))
    for budget_asset, budget_expenses in budget_expense_asset_map.items():
        if len(budget_expenses) == 1:
            Const.FORECAST_BUDGET_EXPENSE_MAP[budget_asset] = budget_expenses[0]
        elif Const.BUDGET_ACCOUNT in budget_asset:
            Const.FORECAST_BUDGET_EXPENSE_MAP[budget_asset] = "{}:{}".format(Const.EXPENSES_ACCOUNT,
                                                                             budget_asset.replace(
                                                                                 "{}:".format(Const.BUDGET_ACCOUNT),
                                                                                 '') or Const.BUDGET_ACCOUNT.replace(
                                                                                 "{}:".format(Const.ASSETS_ACCOUNT),
                                                                                 ''))
        elif Const.SAVING_ACCOUNT in budget_asset:
            Const.FORECAST_BUDGET_EXPENSE_MAP[budget_asset] = "{}:{}".format(Const.EXPENSES_ACCOUNT,
                                                                             budget_asset.replace(
                                                                                 "{}:".format(Const.SAVING_ACCOUNT),
                                                                                 '').replace(
                                                                                 "{}:".format(Const.ASSETS_ACCOUNT),
                                                                                 '') or Const.SAVING_ACCOUNT.replace(
                                                                                 "{}:".format(Const.ASSETS_ACCOUNT),
                                                                                 ''))

    # utils.print_debug(Const.IGNORE_PAYPALS)
    # utils.print_debug(Const.IGNORE_PAYPALS_MAP)
    # utils.print_debug(Const.UNKNOWN_PAYPALS)
    # utils.print_debug(Const.UNKNOWN_PAYPALS_MAP)
    # utils.print_debug(Const.IGNORE_AMAZONS)
    # utils.print_debug(Const.BUDGET_DATA_MAP)
    # utils.print_debug(budget_expense_asset_map)
    # utils.print_debug(Const.FORECAST_BUDGET_EXPENSE_MAP)


def init_accounts(config):
    Const.ACCOUNTS = set()
    Const.ACCOUNTS.add(Const.EXPENSES_ACCOUNT)
    Const.ACCOUNTS.add(Const.ASSETS_ACCOUNT)
    Const.ACCOUNTS.add(Const.CHECKING_ACCOUNT)
    Const.ACCOUNTS.add(Const.LIABILITIES_ACCOUNT)
    Const.ACCOUNTS.add(Const.EQUITY_ACCOUNT)
    Const.ACCOUNTS.add(Const.OPENING_ACCOUNT)
    Const.ACCOUNTS.add(Const.EXPENSE_PAYPAL_UNKNOWN_ACCOUNT)
    Const.ACCOUNTS.add(Const.EXPENSE_AMAZON_UNKNOWN_ACCOUNT)
    Const.ACCOUNTS.add(Const.EXPENSE_UNKNOWN_ACCOUNT)
    Const.ACCOUNTS.add(Const.CASH_ACCOUNT)
    Const.ACCOUNTS.add(Const.SALERY_ACCOUNT)
    Const.ACCOUNTS.add(Const.BUDGET_ACCOUNT)
    Const.ACCOUNTS.add(Const.SAVING_ACCOUNT)

    Const.ACCOUNTS_TITLE[Const.EXPENSES_ACCOUNT] = 'Expenses'
    Const.ACCOUNTS_TITLE[Const.ASSETS_ACCOUNT] = 'Assets'
    Const.ACCOUNTS_TITLE[Const.CHECKING_ACCOUNT] = 'Cechking'
    Const.ACCOUNTS_TITLE[Const.LIABILITIES_ACCOUNT] = 'Liabilities'
    Const.ACCOUNTS_TITLE[Const.EQUITY_ACCOUNT] = 'Eqity'
    Const.ACCOUNTS_TITLE[Const.OPENING_ACCOUNT] = 'Opening'
    Const.ACCOUNTS_TITLE[Const.EXPENSE_PAYPAL_UNKNOWN_ACCOUNT] = 'PayPal'
    Const.ACCOUNTS_TITLE[Const.EXPENSE_AMAZON_UNKNOWN_ACCOUNT] = 'Amazon'
    Const.ACCOUNTS_TITLE[Const.EXPENSE_UNKNOWN_ACCOUNT] = 'Unknow'
    Const.ACCOUNTS_TITLE[Const.CASH_ACCOUNT] = 'Cash'
    Const.ACCOUNTS_TITLE[Const.SALERY_ACCOUNT] = 'Salery'
    Const.ACCOUNTS_TITLE[Const.BUDGET_ACCOUNT] = 'Budget'
    Const.ACCOUNTS_TITLE[Const.SAVING_ACCOUNT] = 'Saving'
    Const.ACCOUNTS_TITLE[Const.UNBUDGET_ACCOUNT] = 'Unbudget'

    if 'define_accounts' in config:
        for account in config['define_accounts']:
            Const.ACCOUNTS.add(account['account'])
            if 'title' in account:
                Const.ACCOUNTS_TITLE[account.get('account', None)] = account['title']

    if 'accounts' in config:
        for key, amount in config['accounts'].items():
            Const.ACCOUNTS.add(amount)

    if 'amazon_rules' in config:
        for rule in config['amazon_rules']:
            Const.ACCOUNTS.add(rule.get('account1', rule.get('account', None)))
            Const.ACCOUNTS.add(rule.get('account2', rule.get('account', None)))
            if 'title' in rule:
                if rule.get('account1', rule.get('account', None)):
                    Const.ACCOUNTS_TITLE[rule.get('account1', rule.get('account', None))] = rule['title']
                if rule.get('account2', rule.get('account', None)):
                    Const.ACCOUNTS_TITLE[rule.get('account2', rule.get('account', None))] = rule['title']
    if 'paypal_rules' in config:
        for rule in config['paypal_rules']:
            Const.ACCOUNTS.add(rule.get('account1', rule.get('account', None)))
            Const.ACCOUNTS.add(rule.get('account2', rule.get('account', None)))
            if 'title' in rule:
                if rule.get('account1', rule.get('account', None)):
                    Const.ACCOUNTS_TITLE[rule.get('account1', rule.get('account', None))] = rule['title']
                if rule.get('account2', rule.get('account', None)):
                    Const.ACCOUNTS_TITLE[rule.get('account2', rule.get('account', None))] = rule['title']
    if 'common_rules' in config:
        for rule in config['common_rules']:
            Const.ACCOUNTS.add(rule.get('account1', rule.get('account', None)))
            Const.ACCOUNTS.add(rule.get('account2', rule.get('account', None)))
            if 'title' in rule:
                if rule.get('account1', rule.get('account', None)):
                    Const.ACCOUNTS_TITLE[rule.get('account1', rule.get('account', None))] = rule['title']
                if rule.get('account2', rule.get('account', None)):
                    Const.ACCOUNTS_TITLE[rule.get('account2', rule.get('account', None))] = rule['title']
    if 'post_common_rules' in config:
        for rule in config['post_common_rules']:
            Const.ACCOUNTS.add(rule.get('account1', rule.get('account', None)))
            Const.ACCOUNTS.add(rule.get('account2', rule.get('account', None)))
            if 'title' in rule:
                if rule.get('account1', rule.get('account', None)):
                    Const.ACCOUNTS_TITLE[rule.get('account1', rule.get('account', None))] = rule['title']
                if rule.get('account2', rule.get('account', None)):
                    Const.ACCOUNTS_TITLE[rule.get('account2', rule.get('account', None))] = rule['title']

    if 'transactions' in config:
        for transaction in config['transactions']:
            if 'expense' in transaction:
                Const.ACCOUNTS.add(transaction['expense'])
            if 'asset' in transaction:
                Const.ACCOUNTS.add(transaction['asset'])

    if 'yearly' in config and 'budget' in config['yearly']:
        for budget in config['yearly']['budget']:
            Const.ACCOUNTS.add(budget['account'])
            if 'title' in budget:
                if 'account' in rule:
                    Const.ACCOUNTS_TITLE[rule['account']] = budget['title']
                if 'account' in budget:
                    Const.ACCOUNTS_TITLE[budget['account']] = budget['title']
        for budget in config['monthly']['budget']:
            Const.ACCOUNTS.add(budget['account'])
            if 'title' in budget:
                if 'account' in rule:
                    Const.ACCOUNTS_TITLE[rule['account']] = budget['title']
                if 'account' in budget:
                    Const.ACCOUNTS_TITLE[budget['account']] = budget['title']

    # if 'paypal' in config and 'payee' in config['paypal']:
    #    Const.ACCOUNTS.add("{}:{}".format(Const.EXPENSES_ACCOUNT, config['paypal']['payee'].strip()))

    # if 'amazon' in config and 'payee' in config['amazon']:
    #    Const.ACCOUNTS.add("{}:{}".format(Const.EXPENSES_ACCOUNT, config['amazon']['payee'].strip()))

    Const.ACCOUNTS = list(filter(None, Const.ACCOUNTS))
    Const.ACCOUNTS.sort()

    for a in Const.ACCOUNTS:
        if not a in Const.ACCOUNTS_TITLE:
            utils.print_verbose("'{:s}' is missing in ACCOUNTS_TITLE".format(a))


def main():
    args = docopt(__doc__)
    colorama.init()
    Const.VERBOSE = args['--verbose']

    # utils.print_debug(args)

    if '--hledger-path' in args and args['--hledger-path']:
        Const.HLEDGER = args['--hledger-path']

    if '--ledger2beancount-path' in args and args['--ledger2beancount-path']:
        Const.LEDGER2BEANCOUNT = args['--ledger2beancount-path']

    if '--strict' in args and args['--strict']:
        Const.HLEDGER_STRICT = args['--strict']

    if '--input-csv-delimiter' in args and args['--input-csv-delimiter']:
        Const.CSV_INPUT_DELIMITER = args['--input-csv-delimiter']

    if '--all-months' in args:
        Const.GEN_ALL_MONTHS = args['--all-months']
    if '--opening' in args or '--opening-closing' in args:
        Const.GEN_OPENINGS = ('--opening' in args and args['--opening']) or (
                '--opening-closing' in args and args['--opening-closing'])
    if '--opening-closing' in args:
        Const.GEN_CLOSINGS_AND_OPENINGS = args['--opening-closing']

    if '--output-dir' in args and args['--output-dir']:
        Const.OUTPUT_DIR = args['--output-dir']
        Const.JOURNALS_PATH = os.path.join(Const.OUTPUT_DIR, 'journals/')
        Const.RULES_PATH = os.path.join(Const.OUTPUT_DIR, 'journals/rules/')
        Const.YEAR_RULES_PATH_FORMAT = os.path.join(Const.OUTPUT_DIR, "journals/{}/rules")
        Const.YEAR_JOURNALS_PATH_FORMAT = os.path.join(Const.OUTPUT_DIR, "journals/{}")
        Const.SOURCE_PATH = os.path.join(Const.OUTPUT_DIR, 'source/')
        Const.INPUT_PATH = os.path.join(Const.OUTPUT_DIR, 'input/')
        Const.YEAR_INPUT_PATH_FORMAT = os.path.join(Const.OUTPUT_DIR, "input/{}")

    if '--templates-dir' in args and args['--templates-dir']:
        Const.TEMPLATES_DIR = args['--templates-dir']
        Const.AMAZON_CSV_RULES_TEMPLATE_FILENAME = os.path.join(
            Const.TEMPLATES_DIR, 'amazon.csv.rules')
        Const.BANK_CSV_RULES_TEMPLATE_FILENAME = os.path.join(
            Const.TEMPLATES_DIR, 'bank.csv.rules')
        Const.COMMON_CSV_RULES_TEMPLATE_FILENAME = os.path.join(
            Const.TEMPLATES_DIR, 'common.csv.rules')
        Const.PAYPAL_CSV_RULES_TEMPLATE_FILENAME = os.path.join(
            Const.TEMPLATES_DIR, 'paypal.csv.rules')
        Const.POST_COMMON_CSV_RULES_TEMPLATE_FILENAME = os.path.join(
            Const.TEMPLATES_DIR, 'post-common.csv.rules')
        Const.TRANSACTION_MOD_HLEDGER_TEMPLATE_FILENAME = os.path.join(
            Const.TEMPLATES_DIR, 'transaction-mod.hledger')

    config_filename = 'config.yml'
    if '-c' in args and args['-c']:
        config_filename = args['-c']

    if not os.path.exists(config_filename):
        utils.print_error("config yml file not found: {}".format(config_filename))
        return 2

    with open(config_filename) as file:
        config = yaml.safe_load(file)

        init_globals(config)
        init_accounts(config)

        if args['accounts']:
            print('\n'.join(Const.ACCOUNTS))
            return 0
        elif args['beancount-options']:
            print(gen_beancount_options(config))
            return 0
        elif args['gen-all']:
            os.makedirs(Const.JOURNALS_PATH, exist_ok=True)

            return gen_all_journal_cmd(config, args)
        elif args['gen-all-forecast']:
            os.makedirs(Const.JOURNALS_PATH, exist_ok=True)

            return gen_all_forecast_cmd(config, args)
        elif args['gen-rules']:
            os.makedirs(Const.JOURNALS_PATH, exist_ok=True)

            year_str = args['<year>']
            if year_str:
                if not year_str.isnumeric():
                    utils.print_error('year must be a number')
                    return 3
            else:
                year_str = None
                os.makedirs(Const.RULES_PATH, exist_ok=True)

            gen_rules(config, year_str)
            return 0
        elif args['gen-month']:
            if not os.path.exists(Const.HLEDGER):
                utils.print_error("hledger nor found: {}".format(Const.HLEDGER))
                return 1

            os.makedirs(Const.JOURNALS_PATH, exist_ok=True)
            return gen_month_cmd(config, args)
        elif args['gen-year']:
            if not os.path.exists(Const.HLEDGER):
                utils.print_error("hledger nor found: {}".format(Const.HLEDGER))
                return 1

            os.makedirs(Const.JOURNALS_PATH, exist_ok=True)
            return gen_year_cmd(config, args)
        elif args['clean-up-csv']:
            os.makedirs(Const.SOURCE_PATH, exist_ok=True)
            if args['<month>']:
                return cleanup_month_csv_cmd(config, args)
            elif args['<year>']:
                return cleanup_year_csv_cmd(config, args)
        elif args['plot-senkey']:
            return plot_senkey_cmd(config, args)
        elif args['plot-senkey-budget']:
            return plot_senkey_budget_cmd(config, args)
        elif args['plot-senkey-expenses']:
            return plot_senkey_expenses_cmd(config, args)
        elif args['plot-senkey-income-budget']:
            return plot_senkey_income_budget_cmd(config, args)
        elif args['budget']:
            return print_budget_balance_cmd(config, args)
        elif args['gen-all']:
            return gen_all_journal_cmd(config, args)
        elif args['beancount']:
            return gen_beancount_cmd(config, args)

    return 0
