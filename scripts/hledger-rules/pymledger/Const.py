import os

VERSION = '3.0.0'
DEBUG = True
VERBOSE = True

WORK_DIR = os.getcwd()
TEMPLATES_DIR = os.path.join(WORK_DIR, 'templates')

HLEDGER = 'hledger'
HLEDGER_STRICT = False
LEDGER2BEANCOUNT = 'ledger2beancount'
JOURNAL_EXT = 'hledger'

OUTPUT_DIR = '.'
JOURNALS_PATH = './journals/'
RULES_PATH = './journals/rules/'
YEAR_RULES_PATH_FORMAT = "./journals/{}/rules"
YEAR_JOURNALS_PATH_FORMAT = "./journals/{}"
SOURCE_PATH = './source/'
INPUT_PATH = './input/'
YEAR_INPUT_PATH_FORMAT = "./input/{}"

AMAZON_CSV_RULES_TEMPLATE_FILENAME = os.path.join(
    TEMPLATES_DIR, 'amazon.csv.rules')
BANK_CSV_RULES_TEMPLATE_FILENAME = os.path.join(
    TEMPLATES_DIR, 'bank.csv.rules')
COMMON_CSV_RULES_TEMPLATE_FILENAME = os.path.join(
    TEMPLATES_DIR, 'common.csv.rules')
PAYPAL_CSV_RULES_TEMPLATE_FILENAME = os.path.join(
    TEMPLATES_DIR, 'paypal.csv.rules')
POST_COMMON_CSV_RULES_TEMPLATE_FILENAME = os.path.join(
    TEMPLATES_DIR, 'post-common.csv.rules')
TRANSACTION_MOD_HLEDGER_TEMPLATE_FILENAME = os.path.join(
    TEMPLATES_DIR, 'transaction-mod.hledger')

AMAZON_CSV_RULES_FILENAME = 'amazon.csv.rules'
BANK_CSV_RULES_FILENAME = 'bank.csv.rules'
COMMON_CSV_RULES_FILENAME = 'common.csv.rules'
PAYPAL_CSV_RULES_FILENAME = 'paypal.csv.rules'
POST_COMMON_CSV_RULES_FILENAME = 'post-common.csv.rules'
TRANSACTION_MOD_HLEDGER_FILENAME = 'transaction-mod.hledger'

INCOME_ACCOUNT = 'income'
EXPENSES_ACCOUNT = 'expenses'
ASSETS_ACCOUNT = 'assets'
LIABILITIES_ACCOUNT = 'liabilities'
EQUITY_ACCOUNT = 'equity'
OPENING_ACCOUNT = 'equity:opening/closing balances'
CLOSING_ACCOUNT = OPENING_ACCOUNT
CHECKING_ACCOUNT = 'assets:bank:checking'
EXPENSE_PAYPAL_UNKNOWN_ACCOUNT = 'expenses:unknown:PayPal'
EXPENSE_AMAZON_UNKNOWN_ACCOUNT = 'expenses:unknown:Amazon'
CASH_ACCOUNT = 'assets:Cash'
EXPENSE_UNKNOWN_ACCOUNT = 'expenses:unknown'
SALERY_ACCOUNT = 'income:salary'
BUDGET_ACCOUNT = 'assets:bank:budget'
SAVING_ACCOUNT = 'assets:bank:saving'
UNBUDGET_ACCOUNT = 'assets:bank:unbudget'

CURRENCY = 'EUR'
COMMODITY = '1000,00 EUR'
DECIMAL_MARK = ','

ROW_NAME_BOOKING_DATE = 'Buchungstag'
ROW_NAME_VAL_DATE = 'Valutadatum'
ROW_NAME_BOOKINGTEXT = 'Buchungstext'
ROW_NAME_BOOKINGDATE = 'Buchungstag'
ROW_NAME_USE = 'Verwendungszweck'
ROW_NAME_REFERENCE = 'Kundenreferenz (End-to-End)'
ROW_NAME_RECIPIENT = 'Beguenstigter/Zahlungspflichtiger'
ROW_NAME_CURRENCY = 'Waehrung'
ROW_NAME_VALUE = 'Betrag'
ROW_NAME_INFO = 'Info'

CSV_INPUT_DELIMITER = ','
CSV_DELIMITER = ','
CSV_QUOTECHAR = '"'

RULE_FIELD_NAME_RECIPIENT = 'beguenstigter_zahlungspflichtiger'
RULE_FIELD_NAME_BOOKINGTEXT = 'buchungstext'
RULE_FIELD_NAME_PAYEE = 'payee'

PAYPAL_PREFIX = 'PP.6330.PP'
PAYPAL_SUFFIX = 'PayPal'
ALT_PAYPAL_SUFFIX = 'PAYPAL'
PAYEE_PAYPAL = '%payee'
PAYEE_AMAZON = '%payee'

GEN_ALL_MONTHS = False
GEN_OPENINGS = False
GEN_CLOSINGS_AND_OPENINGS = False

FORECAST_BUDGET_EXPENSE_MAP = {}
ACCOUNTS = set()
ACCOUNTS_TITLE = {}
IGNORE_AMAZONS = []
IGNORE_PAYPALS = []
UNKNOWN_PAYPALS_MAP = {}
IGNORE_PAYPALS_MAP = {}
UNKNOWN_PAYPALS = []
BUDGET_DATA_MAP = {}
