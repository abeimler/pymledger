import os

from pymledger import Const, utils, HledgerTemplates as Templates


def get_open_year_balance(last_year, last_year_filename):
    cmd = [Const.HLEDGER, 'close', '-s' if Const.HLEDGER_STRICT else '', '-f', last_year_filename, '--auto', '--open',
           '-p', "{:04}".format(last_year), '--open-acct', '"{}"'.format(Const.OPENING_ACCOUNT), '--open-desc',
           '"{}"'.format(Templates.OPENING_DESCRIPTION_FORMAT.format(year=last_year + 1)), Const.ASSETS_ACCOUNT,
           Const.LIABILITIES_ACCOUNT]
    utils.print_info(' '.join(cmd))
    result = os.popen(' '.join(cmd)).read()
    # utils.print_debug(result)
    return result


def get_close_year_balance(year, open_year_filename):
    cmd = [Const.HLEDGER, 'close', '-s' if Const.HLEDGER_STRICT else '', '-f', open_year_filename, '--auto', '--close',
           '-p', "{:04}".format(year), '--close-acct', '"{}"'.format(Const.CLOSING_ACCOUNT), '--close-desc',
           '"{}"'.format(Templates.CLOSING_DESCRIPTION_FORMAT.format(year=year, next_year=year + 1)),
           Const.ASSETS_ACCOUNT, Const.LIABILITIES_ACCOUNT]
    utils.print_info(' '.join(cmd))
    result = os.popen(' '.join(cmd)).read()
    # utils.print_debug(result)
    return result


def get_open_month_balance(year, month, last_month_filename):
    last_year = year
    last_month = month - 1
    if month == 1:
        last_year = year - 1
        last_month = 12
    last_day = "{:04}-{:02}-{:02}".format(year, month, 1)
    peroid = "{:04}-{:02}".format(last_year, last_month)

    cmd = [Const.HLEDGER, 'close', '-s' if Const.HLEDGER_STRICT else '', '-f', last_month_filename, '--auto', '--open',
           '-p', peroid, '--open-acct', Const.OPENING_ACCOUNT, '--open-desc',
           '"{}"'.format(Templates.OPENING_MONTH_DESCRIPTION_FORMAT.format(year=year, month=month)),
           Const.ASSETS_ACCOUNT, Const.LIABILITIES_ACCOUNT]
    utils.print_debug(' '.join(cmd))
    result = os.popen(' '.join(cmd)).read()
    # utils.print_debug(result)
    return result


def get_close_month_balance(year, month, open_month_filename):
    next_year = year
    next_month = month + 1
    if month == 12:
        next_year = year + 1
        next_month = 1
    last_day = "{:04}-{:02}-{:02}".format(next_year, next_month, 1)
    peroid = "{:04}-{:02}".format(year, month)

    cmd = [Const.HLEDGER, 'close', '-s' if Const.HLEDGER_STRICT else '', '-f', open_month_filename, '--auto', '-p',
           peroid, '--close', '--close-acct', Const.CLOSING_ACCOUNT, '--close-desc', '"{}"'.format(
            Templates.CLOSING_MONTH_DESCRIPTION_FORMAT.format(year=year, month=month, next_year=next_year,
                                                              next_month=next_month)), Const.ASSETS_ACCOUNT,
           Const.LIABILITIES_ACCOUNT]
    utils.print_debug(' '.join(cmd))
    result = os.popen(' '.join(cmd)).read()
    # utils.print_debug(result)
    return result


def amount_to_journal_amount_string(amount):
    if isinstance(amount, str):
        return amount.replace('.', Const.DECIMAL_MARK)
    if isinstance(amount, int):
        return "{},00".format(amount)
    if isinstance(amount, float):
        if abs(float(amount) - int(amount) * 100.0) <= 9.00:
            return "{:01}0".format(amount).replace('.', Const.DECIMAL_MARK)
        elif abs(float(amount) - int(amount) * 100.0) <= 99.00:
            return "{:02}".format(amount).replace('.', Const.DECIMAL_MARK)
        elif abs(float(amount) - int(amount)) == 0.0:
            return ("{}" + Const.DECIMAL_MARK + "00").format(int(amount))
        else:
            return "{}".format(amount).replace('.', Const.DECIMAL_MARK)
    return str(amount).replace('.', Const.DECIMAL_MARK)


def is_amount_whole(amount):
    if isinstance(amount, str):
        return amount.replace('.', Const.DECIMAL_MARK).find(Const.DECIMAL_MARK) >= 0
    if isinstance(amount, int):
        return True
    if isinstance(amount, float):
        if abs(float(amount) - int(amount)) == 0.0:
            return True
    return False


def amount_to_rule_string(amount):
    if isinstance(amount, str):
        return amount.replace('.', Const.DECIMAL_MARK)
    if isinstance(amount, int):
        return "{}{}00".format(amount, Const.DECIMAL_MARK)
    if isinstance(amount, float):
        if abs(float(amount) - int(amount)) == 0.0:
            return "{}{}00".format(int(amount), Const.DECIMAL_MARK)
        elif abs(float(amount) - int(amount) * 100.0) <= 9.00:
            return "{:01}".format(amount).replace('.', Const.DECIMAL_MARK)
        elif abs(float(amount) - int(amount) * 100.0) <= 99.00:
            return "{:02}".format(amount).replace('.', Const.DECIMAL_MARK)
        else:
            return "{}".format(amount).replace('.', Const.DECIMAL_MARK)
    return str(amount).replace('.', Const.DECIMAL_MARK)


def amount_to_csv_string(amount):
    if isinstance(amount, str):
        return amount.replace('.', Const.DECIMAL_MARK)
    if isinstance(amount, int):
        return "{}".format(amount)
    if isinstance(amount, float):
        if abs(float(amount) - int(amount)) == 0.0:
            return "{}".format(int(amount))
        elif abs(float(amount) - int(amount) * 100.0) <= 9.00:
            return "{:01}".format(amount).replace('.', Const.DECIMAL_MARK)
        elif abs(float(amount) - int(amount) * 100.0) <= 99.00:
            return "{:02}".format(amount).replace('.', Const.DECIMAL_MARK)
        else:
            return "{}".format(amount).replace('.', Const.DECIMAL_MARK)
    return str(amount).replace('.', Const.DECIMAL_MARK)


def string_to_amount_value(s):
    if isinstance(s, str):
        return float(s.replace(Const.DECIMAL_MARK, '.'))
    return float(str(s).replace(Const.DECIMAL_MARK, '.'))


def extend_if_conds_with_amount(if_conds, rule):
    amount = rule['amount'] if 'amount' in rule and rule['amount'] else None
    csv_amount_1 = amount_to_rule_string(rule['amount']) if 'amount' in rule and rule['amount'] else None
    csv_amount_2 = amount_to_csv_string(rule['amount']) if 'amount' in rule and rule['amount'] else None
    currency = rule['currency'] if 'currency' in rule else None
    income = rule['income'] if 'income' in rule else False

    new_if_conds = []
    if csv_amount_1 or csv_amount_2:
        for if_cond in if_conds:
            prefix = '-' if income else ''
            if csv_amount_1 and not is_amount_whole(amount):
                new_if_conds.append(if_cond + ".*, {}{}".format(prefix, csv_amount_1))
            if csv_amount_2:
                new_if_conds.append(if_cond + ".*,{}{}".format(prefix, csv_amount_2))
    else:
        new_if_conds = if_conds

    for i in range(len(new_if_conds)):
        if currency:
            new_if_conds[i] = new_if_conds[i] + ',' + currency

    return new_if_conds
