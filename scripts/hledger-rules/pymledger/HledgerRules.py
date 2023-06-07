import os
from string import Template

from pymledger import Const, utils, HledgerTemplates as Templates
from pymledger.HledgerUtils import amount_to_rule_string


def sort_rule_element(elem):
    if 'name' in elem and 'account' in elem:
        return "{}:{}".format(elem['account'], elem['name'])
    return elem['account']


def gen_rule(if_conds, description, **kwargs):
    if not isinstance(if_conds, list) or isinstance(if_conds, str):
        if if_conds:
            if_conds = [if_conds]

    account1 = None
    account1_name = 'account1'
    account2 = None
    account2_name = 'account2'
    income = False
    pre = ''
    file_comment = ''
    comment = ''
    tags = []
    code = None
    payee = "%{}".format(Const.RULE_FIELD_NAME_PAYEE)

    for k, v in kwargs.items():
        if k == 'pre' and v:
            pre = v
        if k == 'account' and v:
            account1 = v.strip()
        elif k == 'account_name' and v:
            account1_name = v
        elif k == 'account1' and v:
            account1 = v.strip()
        elif k == 'account1_name' and v:
            account1_name = v
        elif k == 'account2' and v:
            account2 = v.strip()
        elif k == 'account2_name' and v:
            account2_name = v
        elif k == 'income' and v:
            income = True
        elif k == 'file_comment' and v:
            file_comment = ";;{}".format(v)
        elif k == 'comment' and v:
            comment = v
        elif k == 'tags' and v:
            for t in v:
                if t[-1] != ':' and ':' not in t:
                    t = t + ':'
                tags.append(t.replace(',', '').replace('\n', ' '))
        elif k == 'code' and v:
            code = v.strip()
        elif k == 'payee' and v:
            payee = v.strip()

    if if_conds:
        conds = ''
        if if_conds:
            if pre and if_conds:
                conds = "{}\n{}".format(if_conds[0], pre) + ("\n{}".format(pre)).join(if_conds[1:]).rstrip('\n')
            else:
                conds = '\n'.join(if_conds).rstrip('\n')

        accounts = ''
        if account1:
            accounts = accounts + pre + Templates.RULE_ACCOUNT_ENTRY_FORMAT.format(name=account1_name, account=account1)
        if account2:
            accounts = accounts + pre + Templates.RULE_ACCOUNT_ENTRY_FORMAT.format(name=account2_name, account=account2)
        if income:
            accounts = accounts + pre + Templates.RULE_ACCOUNT_ENTRY_FORMAT.format(name='amount', account='%amount')

        if comment:
            if tags:
                comment = "{} {}".format(comment, Templates.DEFAULT_RULE_COMMENT_ENTRY_FORMAT.format(
                    bookingtext="%{}".format(Const.RULE_FIELD_NAME_BOOKINGTEXT),
                    payee=payee) + ', ' + ', '.join(tags))

            if code:
                return Templates.RULE_WITH_CODE_AND_COMMENT_ENTRY_TEMPLATE.substitute(pre=pre, conds=conds,
                                                                                      description=description.strip(),
                                                                                      accounts=accounts,
                                                                                      file_comment=file_comment,
                                                                                      comment=comment, code=code)
            else:
                return Templates.RULE_WITH_COMMENT_ENTRY_TEMPLATE.substitute(pre=pre, conds=conds,
                                                                             description=description.strip(),
                                                                             accounts=accounts,
                                                                             file_comment=file_comment, comment=comment)
        elif tags:
            comment = Templates.DEFAULT_RULE_COMMENT_ENTRY_FORMAT.format(
                bookingtext="%{}".format(Const.RULE_FIELD_NAME_BOOKINGTEXT),
                payee=payee.replace(',', '').replace('\n', ' ')) + ', ' + ', '.join(tags)
            if code:
                return Templates.RULE_WITH_CODE_AND_COMMENT_ENTRY_TEMPLATE.substitute(pre=pre, conds=conds,
                                                                                      description=description.strip(),
                                                                                      accounts=accounts,
                                                                                      file_comment=file_comment,
                                                                                      comment=comment, code=code)
            else:
                return Templates.RULE_WITH_COMMENT_ENTRY_TEMPLATE.substitute(pre=pre, conds=conds,
                                                                             description=description.strip(),
                                                                             accounts=accounts,
                                                                             file_comment=file_comment, comment=comment)
        else:
            if code:
                return Templates.RULE_WITH_CODE_ENTRY_TEMPLATE.substitute(pre=pre, conds=conds,
                                                                          description=description.strip(),
                                                                          accounts=accounts, file_comment=file_comment,
                                                                          comment=comment, code=code)
            else:
                return Templates.RULE_ENTRY_TEMPLATE.substitute(pre=pre, conds=conds, description=description.strip(),
                                                                accounts=accounts, file_comment=file_comment,
                                                                comment=comment)
    elif file_comment:
        return "{}\n".format(file_comment)

    return ''


def gen_transaction_mod(query, account, **kwargs):
    not_query = ''
    date_query = ''
    amount = -1

    for k, v in kwargs.items():
        if (k == 'not_acct' or k == 'not_account') and v:
            not_query = 'not:acct:"{}"'.format(v).strip()
        elif (k == 'not_query' or k == 'not') and v:
            not_query = "not:{}".format(v).strip()
        elif k == 'date' and v:
            date_query = 'date:"{}"'.format(v)
        elif k == 'not_date' and v:
            date_query = 'not:date:"{}"'.format(v)
        elif k == 'amount' and v:
            amount = v

    if query and ' ' in query:
        if query[0] != '"':
            query = '"' + query
        if query[-1] != '"':
            query = query + '"'

    if account:
        if not_query:
            return Templates.TRANSACTION_MOD_ENTRY_WITH_NOT_TEMPLATE.substitute(query=query.strip(),
                                                                                account=Templates.ACCOUNT_FORMAT.format(
                                                                                    account=account.strip()),
                                                                                not_query=not_query,
                                                                                date_query=date_query,
                                                                                amount=amount)
        if query:
            return Templates.TRANSACTION_MOD_ENTRY_TEMPLATE.substitute(query=query.strip(),
                                                                       account=Templates.ACCOUNT_FORMAT.format(
                                                                           account=account.strip()),
                                                                       date_query=date_query,
                                                                       amount=amount)

    return ''


def gen_common_rules(rules_config, ignore_name_key=False):
    common_rules = ''
    if rules_config:
        for common_rule in rules_config:
            if_conds = []
            if 'if' in common_rule:
                ifs = common_rule['if']
                if not isinstance(ifs, list) or isinstance(ifs, str):
                    ifs = [common_rule['if']]
                if_conds.extend(ifs)
            if 'name' in common_rule and not ignore_name_key:
                names = common_rule['name']
                if not isinstance(names, list) or isinstance(names, str):
                    names = [common_rule['name']]
                for name in names:
                    if_conds.append("KARTENZAHLUNG.*{}".format(name, name, name))
                    if_conds.append("LASTSCHRIFT.*{}".format(name, name, name))
                    if_conds.append("RECHNUNG.*{}".format(name, name, name))
                    if_conds.append("UEBERWEISUNG.*{}".format(name, name, name))
            if 'payment_name' in common_rule:
                names = common_rule['payment_name']
                if not isinstance(names, list) or isinstance(names, str):
                    names = [common_rule['payment_name']]
                for name in names:
                    if_conds.append("KARTENZAHLUNG.*{}".format(name, name, name))
                    if_conds.append("LASTSCHRIFT.*{}".format(name, name, name))
                    if_conds.append("RECHNUNG.*{}".format(name, name, name))
                    if_conds.append("UEBERWEISUNG.*{}".format(name, name, name))
            if 'invoice_name' in common_rule:
                names = common_rule['invoice_name']
                if not isinstance(names, list) or isinstance(names, str):
                    names = [common_rule['invoice_name']]
                for name in names:
                    if_conds.append("RECHNUNG.*{}".format(name, name, name))
            description = Templates.CSV_DESCRIPTION_PAYEE_FORMAT.format(payee_field=Const.RULE_FIELD_NAME_RECIPIENT,
                                                                        description=common_rule.get('description', ''))
            if 'payee_description' in common_rule:
                description = common_rule['payee_description']
            common_rules = common_rules + gen_rule(if_conds, description, account=common_rule.get('account'),
                                                   account1=common_rule.get('account1'),
                                                   account2=common_rule.get('account2'),
                                                   income=common_rule.get('income'))

        for common_rule in rules_config:
            if_conds = []
            if 'credit_note' in common_rule:
                names = common_rule['credit_note']
                if not isinstance(names, list) or isinstance(names, str):
                    names = [common_rule['credit_note']]
                for name in names:
                    if_conds.append("GUTSCHR.*{}".format(name))
            description = Templates.CSV_DESCRIPTION_PAYEE_FORMAT.format(payee_field=Const.RULE_FIELD_NAME_RECIPIENT,
                                                                        description=common_rule.get('description', ''))
            if 'payee_description' in common_rule:
                description = common_rule['payee_description']
            common_rules = common_rules + gen_rule(if_conds, description,
                                                   account1=common_rule.get('account1', Const.CHECKING_ACCOUNT),
                                                   account2=common_rule.get('account2', common_rule.get('account')),
                                                   income=True)

    return common_rules


def gen_amazon_rules_content(config, amazon_rules_template):
    amazon_rules = ''
    if 'amazon_rules' in config:
        amazon_rules = gen_common_rules(config['amazon_rules'])
    amazon_rules_content = amazon_rules_template.substitute({'rules': amazon_rules})
    return amazon_rules_content


def gen_paypal_rules_content(config, paypal_rules_template):
    paypal_rules = ''
    if 'paypal_rules' in config:
        paypal_rules = gen_common_rules(config['paypal_rules'], True)
        for paypal_rule in config['paypal_rules']:
            if_conds = []
            names = []
            if 'name' in paypal_rule:
                names = paypal_rule['name']
                if isinstance(names, str):
                    names = [paypal_rule['name'].strip()]
                elif not isinstance(names, list):
                    names = [paypal_rule['name']]
                for name in names:
                    amount = amount_to_rule_string(paypal_rule['amount']) if 'amount' in paypal_rule and paypal_rule[
                        'amount'] else '.*'
                    ref = paypal_rule['ref'] if 'ref' in paypal_rule and paypal_rule['ref'] else '.*'
                    if_conds.append(
                        "{}.*{}.*{}.*{}.*{}".format(Const.PAYPAL_PREFIX, name, Const.PAYPAL_SUFFIX, ref, amount))
                    if_conds.append("{}.*{}.*{}.*{}".format(name, Const.PAYPAL_SUFFIX, ref, amount))
                    if_conds.append("{}.*{}.*{}.*{}".format(name, Const.ALT_PAYPAL_SUFFIX, ref, amount))

            full_description = Templates.PAYPAL_DESCRIPTION_FORMAT.format(description=paypal_rule.get('description'))
            if 'payee' in paypal_rule:
                full_description = Templates.PAYPAL_DESCRIPTION_PAYEE_FORMAT.format(payee=paypal_rule['payee'],
                                                                                    description=paypal_rule.get(
                                                                                        'description'))
            else:
                full_description = Templates.PAYPAL_DESCRIPTION_PAYEE_FORMAT.format(
                    description=paypal_rule.get('description'), payee="%{}".format(Const.RULE_FIELD_NAME_PAYEE))

            tags = []
            if names:
                tags.append("name:{}".format(names[0].replace(',', '').replace('\n', ' ').strip()))
            paypal_rules = paypal_rules + gen_rule(if_conds, full_description, account=paypal_rule.get('account'),
                                                   account1=paypal_rule.get('account1'),
                                                   account2=paypal_rule.get('account2'), payee=paypal_rule.get('payee'),
                                                   tags=tags)

    paypal_rules_content = paypal_rules_template.substitute({'rules': paypal_rules})
    return paypal_rules_content


def gen_common_rules_content(config, common_rules_template):
    common_rules = ''
    if 'common_rules' in config:
        common_rules = gen_common_rules(config['common_rules'])
    common_rules_content = common_rules_template.substitute({'rules': common_rules})
    return common_rules_content


def gen_post_common_rules_content(config, post_common_rules_template):
    post_common_rules = ''
    if 'post_common_rules' in config:
        post_common_rules = gen_common_rules(config['post_common_rules'])
    post_common_rules_content = post_common_rules_template.substitute({'rules': post_common_rules})
    return post_common_rules_content


def gen_bank_rules_content(config, bank_rules_template):
    bank_rules = ''
    if 'bank_rules' in config:
        bank_rules = gen_common_rules(config['bank_rules'])
    bank_rules_content = bank_rules_template.substitute(
        {'rules': bank_rules, 'account_expense_unknown': Const.EXPENSE_UNKNOWN_ACCOUNT,
         'account_checking': Const.CHECKING_ACCOUNT, 'currency': Const.CURRENCY, 'delimiter': Const.CSV_DELIMITER})
    return bank_rules_content


def gen_transaction_mod_rules_content(config, year_str, transaction_mod_hledger_template):
    transaction_mods = ''
    if 'transactions' in config:
        for transaction in config['transactions']:
            if 'expense' in transaction and 'asset' in transaction:
                virtual_asset = Templates.BUDGET_ACCOUNT_FORMAT.format(transaction['asset'].strip())
                query = Templates.ACCOUNT_QUERY_FOTMAT.format(account=transaction['expense'].strip())
                transaction_mods = transaction_mods + gen_transaction_mod(query, virtual_asset,
                                                                          not_acct=transaction.get('not_acct',
                                                                                                   transaction.get(
                                                                                                       'not_account')),
                                                                          date="{}".format(
                                                                              year_str) if year_str else '',
                                                                          amount=1 if 'income' in transaction and transaction['income'] else -1)
    transaction_mod_hledger_content = transaction_mod_hledger_template.substitute({'transactions': transaction_mods})
    return transaction_mod_hledger_content


def gen_rules(config, year_str=None):
    if not os.path.exists(Const.JOURNALS_PATH):
        os.mkdir(Const.JOURNALS_PATH)
        utils.print_verbose("create folder: {}".format(Const.JOURNALS_PATH))
    if not year_str and not os.path.exists(Const.RULES_PATH):
        os.mkdir(Const.RULES_PATH)
        utils.print_verbose("create folder: {}".format(Const.RULES_PATH))

    if year_str and not os.path.exists(Const.YEAR_JOURNALS_PATH_FORMAT.format(year_str)):
        os.mkdir(Const.YEAR_JOURNALS_PATH_FORMAT.format(year_str))
        utils.print_verbose("create folder: {}".format(Const.YEAR_JOURNALS_PATH_FORMAT.format(year_str)))
    if year_str and not os.path.exists(Const.YEAR_RULES_PATH_FORMAT.format(year_str)):
        os.mkdir(Const.YEAR_RULES_PATH_FORMAT.format(year_str))
        utils.print_verbose("create folder: {}".format(Const.YEAR_RULES_PATH_FORMAT.format(year_str)))

    with open(Const.AMAZON_CSV_RULES_TEMPLATE_FILENAME) as template_file:
        utils.print_verbose("read template: {}".format(Const.AMAZON_CSV_RULES_TEMPLATE_FILENAME))
        amazon_rules_template = Template(template_file.read())
        amazon_rules_content = gen_amazon_rules_content(config, amazon_rules_template)
        if year_str:
            amazon_rules_filename = os.path.join(Const.YEAR_RULES_PATH_FORMAT.format(year_str),
                                                 Const.AMAZON_CSV_RULES_FILENAME)
        else:
            amazon_rules_filename = os.path.join(Const.RULES_PATH, Const.AMAZON_CSV_RULES_FILENAME)
        with open(amazon_rules_filename, 'w') as rules_file:
            rules_file.write(amazon_rules_content)
            utils.print_succ("write amazon rules: {}".format(amazon_rules_filename))

    with open(Const.PAYPAL_CSV_RULES_TEMPLATE_FILENAME) as template_file:
        utils.print_verbose("read template: {}".format(Const.AMAZON_CSV_RULES_TEMPLATE_FILENAME))
        paypal_rules_template = Template(template_file.read())
        paypal_rules_content = gen_paypal_rules_content(config, paypal_rules_template)
        if year_str:
            paypal_rules_filename = os.path.join(Const.YEAR_RULES_PATH_FORMAT.format(year_str),
                                                 Const.PAYPAL_CSV_RULES_FILENAME)
        else:
            paypal_rules_filename = os.path.join(Const.RULES_PATH, Const.PAYPAL_CSV_RULES_FILENAME)
        with open(paypal_rules_filename, 'w') as rules_file:
            rules_file.write(paypal_rules_content)
            utils.print_succ("write paypal rules: {}".format(paypal_rules_filename))

    with open(Const.COMMON_CSV_RULES_TEMPLATE_FILENAME) as template_file:
        utils.print_verbose("read template: {}".format(Const.COMMON_CSV_RULES_TEMPLATE_FILENAME))
        common_rules_template = Template(template_file.read())
        common_rules_content = gen_common_rules_content(config, common_rules_template)
        if year_str:
            common_rules_filename = os.path.join(Const.YEAR_RULES_PATH_FORMAT.format(year_str),
                                                 Const.COMMON_CSV_RULES_FILENAME)
        else:
            common_rules_filename = os.path.join(Const.RULES_PATH, Const.COMMON_CSV_RULES_FILENAME)
        with open(common_rules_filename, 'w') as rules_file:
            rules_file.write(common_rules_content)
            utils.print_succ("write common rules: {}".format(common_rules_filename))

    with open(Const.POST_COMMON_CSV_RULES_TEMPLATE_FILENAME) as template_file:
        utils.print_verbose("read template: {}".format(Const.POST_COMMON_CSV_RULES_TEMPLATE_FILENAME))
        post_common_rules_template = Template(template_file.read())
        post_common_rules_content = gen_post_common_rules_content(config, post_common_rules_template)
        post_common_rules_filename = os.path.join(Const.RULES_PATH, Const.POST_COMMON_CSV_RULES_FILENAME)
        if year_str:
            post_common_rules_filename = os.path.join(Const.YEAR_RULES_PATH_FORMAT.format(year_str),
                                                      Const.POST_COMMON_CSV_RULES_FILENAME)
        with open(post_common_rules_filename, 'w') as rules_file:
            rules_file.write(post_common_rules_content)
            utils.print_succ("write post-common rules: {}".format(post_common_rules_filename))

    with open(Const.BANK_CSV_RULES_TEMPLATE_FILENAME) as template_file:
        utils.print_verbose("read template: {}".format(
            Const.BANK_CSV_RULES_TEMPLATE_FILENAME))
        bank_rules_template = Template(template_file.read())
        bank_rules_content = gen_bank_rules_content(config, bank_rules_template)
        if year_str:
            bank_rules_filename = os.path.join(
                Const.YEAR_RULES_PATH_FORMAT.format(year_str), Const.BANK_CSV_RULES_FILENAME)
        else:
            bank_rules_filename = os.path.join(
                Const.RULES_PATH, Const.BANK_CSV_RULES_FILENAME)
        with open(bank_rules_filename, 'w') as rules_file:
            rules_file.write(bank_rules_content)
            utils.print_succ("write bank rules: {}".format(bank_rules_filename))

    with open(Const.TRANSACTION_MOD_HLEDGER_TEMPLATE_FILENAME) as file:
        utils.print_verbose("read template: {}".format(Const.TRANSACTION_MOD_HLEDGER_TEMPLATE_FILENAME))
        transaction_mod_hledger_template = Template(file.read())
        transaction_mod_hledger_content = gen_transaction_mod_rules_content(config, year_str,
                                                                            transaction_mod_hledger_template)
        if year_str:
            transaction_mod_hledger_filename = os.path.join(Const.YEAR_JOURNALS_PATH_FORMAT.format(year_str),
                                                            Const.TRANSACTION_MOD_HLEDGER_FILENAME)
        else:
            transaction_mod_hledger_filename = os.path.join(Const.JOURNALS_PATH, Const.TRANSACTION_MOD_HLEDGER_FILENAME)
        with open(transaction_mod_hledger_filename, 'w') as transaction_mod_file:
            transaction_mod_file.write(transaction_mod_hledger_content)
            utils.print_succ("write transaction mod: {}".format(transaction_mod_hledger_filename))
