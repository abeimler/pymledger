from string import Template

OPENING_DESCRIPTION_FORMAT = "opening balances  ; clopen:{year:04}, opening:"
CLOSING_DESCRIPTION_FORMAT = "closing balances  ; clopen:{year:04}, clclose:{next_year:04}, closing:"
OPENING_MONTH_DESCRIPTION_FORMAT = "opening balances  ; clopen:{year:04}/{month:02}, opening:"
CLOSING_MONTH_DESCRIPTION_FORMAT = "closing balances  ; clopen:{next_year:04}/{next_month:02}, clclose:{year:04}/{month:02}, closing:"
NON_CL_OPENING_DESCRIPTION_FORMAT = "opening balances  ; opening:"

DEFINE_ACCOUNT_TYPE_ENTRY_FORMAT = "account {account:<64}  ; type: {type:1}\n"
DEFINE_ACCOUNT_ENTRY_FORMAT = "account {account:<64}\n"

CSV_RULES_CONTENT_TEAMPLTE = Template(""";;do not change, generated file; month: ${year}-${month}

;; include generated rules
include ../../rules/bank.csv.rules
include ${year}-${month}.bank.amazon.csv.rules
include ${year}-${month}.bank.paypal.csv.rules
include ../../rules/post-common.csv.rules


;;; montly generated rules

${rules}

""")

MONTH_CONTENT_TEMPLATE = Template(""";;do not change, generated file; month: ${year}-${month}

;; define monthly accounts ${year}-${month}
${accounts}

;; include generated journals
include ${year}-${month}.budget.hledger
include ${year}-${month}.bank.hledger
include ${year}-${month}.cash.hledger
include ${year}-${month}.custom.hledger

include ${year}-${month}.reconcile.hledger
""")

OPEN_MONTH_CONTENT_TEMPLATE = Template(""";;do not change, generated file; month: ${year}-${month}

;;; Accounts
;; define default accounts
${default_accounts}
;; define sub accounts
${sub_accounts}

;; define monthly accounts ${year}-${month}
${accounts}

commodity ${commodity}
decimal-mark ${decimal_mark}

;; opening balances
${opening}

;; include generated journals
include ${year}-${month}.hledger

""")

CLOSED_MONTH_CONTENT_TEMPLATE = Template(""";;do not change, generated file; month: ${year}-${month}

;;; Accounts
;; define default accounts
${default_accounts}
;; define sub accounts
${sub_accounts}

;; define monthly accounts ${year}-${month}
${accounts}

commodity ${commodity}
decimal-mark ${decimal_mark}

;; opening balances
${opening}

;; include generated journals
include ${year}-${month}.hledger

;; closing balances
${closing}

""")

YEAR_CONTENT_TEMPLATE = Template(""";;do not change, generated file; year: ${year}

;;; Accounts
;; define default accounts
${default_accounts}
;; define sub accounts
${sub_accounts}

commodity ${commodity}
decimal-mark ${decimal_mark}

Y${year}

include ${year}.budget.hledger

;; monthly journals
${includes}

include transaction-mod.hledger
""")

OPEN_YEAR_CONTENT_TEMPLATE = Template(""";;do not change, generated file; year: ${year}

;;; Accounts
;; define default accounts
${default_accounts}
;; define sub accounts
${sub_accounts}

commodity ${commodity}
decimal-mark ${decimal_mark}

Y${year}

;; opening balances
${opening}

include ${year}.budget.hledger

;; monthly journals
${includes}

include transaction-mod.hledger
""")

CLOSED_YEAR_CONTENT_TEMPLATE = Template(""";;do not change, generated file; year: ${year}

;;; Accounts
;; define default accounts
${default_accounts}
;; define sub accounts
${sub_accounts}

commodity ${commodity}
decimal-mark ${decimal_mark}

Y${year}

;; opening balances
${opening}

include ${year}.budget.hledger

;; monthly journals
${includes}

include transaction-mod.hledger

;; closing balances
${closing}

""")

ALL_CONTENT_TEMPLATE = Template(""";;do not change, generated file
;
; ${title}
;

${opening}

;; journals years here
${includes}

;;; "unbudget" account = checking - budget - saving
account ${unbudget_account}
;${start_year}-01-01 open unbudget       ; clopen:, opening:, unbudget:
;    ${unbudget_account}                     0${decimal_mark}0 ${currency} = 0${decimal_mark}0 ${currency}

;; populate unbudget account
= ${checking_account}                    ; unbudget:
    (${unbudget_account})                   *1
= ${budget_account}                      ; unbudget:
    (${unbudget_account})                   *-1
= ${saving_account}                      ; unbudget:
    (${unbudget_account})                   *-1

;; rebalance bank account, so it's equals checking
= ${budget_account}                      ; unbudget:
    (${bank_account})                       *-1
= ${saving_account}                      ; unbudget:
    (${bank_account})                       *-1
= ${unbudget_account}                    ; unbudget:
    (${bank_account})                       *-1
""")

RECONCILE_CONTENT_TEMPLATE = Template(""";;do not change, generated file; month: ${year}-${month}

;; define monthly accounts ${year}-${month}
${accounts}

commodity ${commodity}
decimal-mark ${decimal_mark}

;; reconciles entires
${entires}
""")

TRANSACTION_MOD_ENTRY_TEMPLATE = Template("""= ${query} ${date_query}
    ${account}                              *${amount}

""")

TRANSACTION_MOD_ENTRY_WITH_NOT_TEMPLATE = Template("""= ${query} ${not_query} ${date_query}
    ${account}                              *${amount}

""")

ACCOUNT_QUERY_FOTMAT = 'acct:"{account}"'

RULE_ENTRY_TEMPLATE = Template("""${file_comment}
${pre}if ${conds}
${pre}    description ${description}
${accounts}
""")
RULE_WITH_CODE_ENTRY_TEMPLATE = Template("""${file_comment}
${pre}if ${conds}
${pre}    description ${description}
${pre}    code ${code}
${accounts}
""")
RULE_WITH_COMMENT_ENTRY_TEMPLATE = Template("""${file_comment}
${pre}if ${conds}
${pre}    description ${description}
${pre}    comment ${comment}
${accounts}
""")
RULE_WITH_CODE_AND_COMMENT_ENTRY_TEMPLATE = Template("""${file_comment}
${pre}if ${conds}
${pre}    description ${description}
${pre}    comment ${comment}
${pre}    code ${code}
${accounts}
""")

ACCOUNT_FORMAT = "{account:<64}"
RULE_ACCOUNT_ENTRY_FORMAT = "    {name:<11} {account:<64}\n"
JOURNAL_ENTRY_FORMAT = "    {account:<64}  {amount:>10} {currency}\n"
JOURNAL_ENTRY_WITH_COMMENT_FORMAT = "    {account:<64}  {amount:>10} {currency} ; {comment}\n"
DESCRIPTION_FORMAT = "{payee} | {description}"

# note: "[account]" not working
BUDGET_ACCOUNT_FORMAT = "({})"
BUDGET_ENTRY_FORMAT = JOURNAL_ENTRY_FORMAT
BUDGET_ENTRY_WITH_COMMENT_FORMAT = JOURNAL_ENTRY_WITH_COMMENT_FORMAT

BUDGET_CONTENT_TEMPLATE = Template(""";;do not change, generated file; ${year}-${month}

;; Budget, from last months salary
= acct:"${account}$$" date:"${date}"
${accounts}
""")
YEAR_BUDGET_CONTENT_TEMPLATE = Template(""";;do not change, generated file; ${year}

;; Budget, from every months salary
= acct:"${account}$$" date:"${date}"
${accounts}
""")

CURRENT_MONTH_BUDGET_CONTENT_TEMPLATE = Template(""";;do not change, generated file; ${year}-${month}

;; Budget
${date} * Current Month Budget ; budget:
${accounts}
""")
CURRENT_YEAR_BUDGET_CONTENT_TEMPLATE = Template(""";;do not change, generated file; ${year}

;; Budget
${entires}
""")
CURRENT_YEAR_BUDGET_CONTENT_ENTRY_TEMPLATE = Template("""${date} * Current Year Budget for month ${month}; budget:
${accounts}
""")

CURRENT_MONTH_BUDGET_CONTENT_EMPTY_TEMPLATE = Template(""";;do not change, generated file; ${year}-${month}

;; Budget
; bank entires are empty, nothing to budget
""")

FORECAST_ACCOUNT_FORMAT = "{}"
FORECAST_ENTRY_FORMAT = JOURNAL_ENTRY_FORMAT
FORECAST_ENTRY_WITH_COMMENT_FORMAT = JOURNAL_ENTRY_WITH_COMMENT_FORMAT
FORECAST_CONTENT_TEMPLATE = Template(""";;do not change, generated file; ${year}-${month}

;; Forecast, for this month ${year}-${month}
~ ${date}
${accounts}
    ${checking}
""")
YEAR_FORECAST_CONTENT_TEMPLATE = Template(""";;do not change, generated file; ${year}

;; Forecast, for this year ${year}
~ ${date}
${accounts}
    ${checking}

;; Budget for this year months
${includes}
""")

CSV_DESCRIPTION_PAYEE_FORMAT = "%{payee_field} | {description}"

PAYPAL_DESCRIPTION_PAYEE_FORMAT = "{payee} | PayPal {description}"
PAYPAL_DESCRIPTION_FORMAT = "PayPal {description}"
PAYPAL_RULES_CONTENT_TEMPLATE = Template(""";;do not change, generated file; ${year}-${month}

;;; PayPal rules
${rules}
""")

AMAZON_DESCRIPTION_PAYEE_FORMAT = "{payee} | Amazon {description}"
AMAZON_DESCRIPTION_FORMAT = "Amazon {description}"
AMAZON_RULES_CONTENT_TEMPLATE = Template(""";;do not change, generated file; ${year}-${month}

;;; Amazon rules
${rules}
""")

CASH_JOURNAL_ENTRY_FORMAT = """{year:04}/{month:02}/{day:02} * {description}
    {account:<64} {amount:>10} {currency}
    {cash_account}
"""
CASH_JOURNAL_ENTRY_WITH_COMMENT_FORMAT = """{year:04}/{month:02}/{day:02} * {description}
    {account:<64} {amount:>10} {currency} ; {comment}
    {cash_account}
"""
CASH_JOURNAL_CONTENT_TEMPLATE = Template(""";;do not change, generated file; ${year}-${month}

;;; Cash entires
${entires}
""")

RECONCILE_DEFAULT_DESCRIPTION_FORMAT = "monthly reconcile  ; reconcile:"
RECONCILE_JOURNAL_ENTRY_FORMAT = """{year:04}/{month:02}/{day:02} {description}
    {account:<64} 0{decimal_mark}0 {currency} = {amount:>10} {currency}
"""

DEFAULT_RULE_COMMENT_ENTRY_FORMAT = "type:{bookingtext}, payee:{payee}"

BEANCOUNT_OPTION_FORMAT = 'option "{option}" "{amount}"'
BEANCOUNT_PLUGIN_FORMAT = 'plugin "{plugin}"'
