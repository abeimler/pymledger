import datetime
from pprint import pprint

from colorama import Fore

from pymledger import Const


def print_info(msg):
    print(Fore.RESET + msg)


def print_warn(msg):
    print(Fore.YELLOW + 'WARN: ' + Fore.RESET + msg)


def print_succ(msg):
    print(Fore.GREEN + msg)


def print_error(msg):
    print(Fore.RED + 'ERROR: ' + Fore.RESET + msg)


def print_debug(msg):
    if Const.DEBUG:
        pprint(msg)


def print_verbose(msg):
    if Const.VERBOSE:
        pprint(Fore.CYAN + msg)


def last_date_of_month(any_date):
    next_month = any_date.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)


def last_day_of_month(year, month):
    return last_date_of_month(datetime.date(year, month, 1)).day
