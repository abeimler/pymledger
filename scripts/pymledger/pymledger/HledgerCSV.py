import csv
import os
import re
from datetime import datetime

from pymledger import Const, utils


def clean_up_input_csv(filename_csv, output_filename_csv):
    out_rows = []
    headers = []
    add_code_field = False
    with open(filename_csv, 'r', newline='') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=Const.CSV_INPUT_DELIMITER, quotechar=Const.CSV_QUOTECHAR)
        r = 1
        for row in reader:
            headers = list(row.keys())
            out_row = row.copy()
            for k, v in out_row.items():
                if k == 'Auftragskonto' or k == 'Glaeubiger ID' or k == 'Sammlerreferenz' or k == 'Lastschrift Ursprungsbetrag' or k == 'Auslagenersatz Ruecklastschrift' or k == 'Kontonummer/IBAN' or k == 'BIC (SWIFT-Code)':
                    out_row[k] = re.sub(r'[a-zA-Z0-9]', '*', v)
                elif k == 'Mandatsreferenz':
                    out_row[k] = re.sub(r'[\S]', '*', v)
                elif k == Const.ROW_NAME_USE:
                    out_row[k] = v.strip()
                elif k == Const.ROW_NAME_BOOKINGDATE:
                    out_row[k] = v.strip()
                elif k == Const.ROW_NAME_REFERENCE:
                    out_row[k] = v.strip()
                elif k == Const.ROW_NAME_RECIPIENT:
                    out_row[k] = v.strip()
                elif k == Const.ROW_NAME_CURRENCY:
                    if v:
                        out_row[k] = v.strip()
                    else:
                        out_rows[k] = Const.CURRENCY
                elif k == Const.ROW_NAME_VALUE:
                    if v:
                        out_row[k] = v.strip()
                    else:
                        out_row[k] = '0'
                elif k == Const.ROW_NAME_INFO:
                    out_row[k] = v.strip()
                elif k == Const.ROW_NAME_VAL_DATE:
                    out_row[k] = v.strip()
                elif k == Const.ROW_NAME_BOOKINGTEXT:
                    out_row[k] = re.sub(r'[\s]+', ' ', v).strip()
                else:
                    out_row[k] = re.sub(r'[\S]', '*', v)

            code = row[Const.ROW_NAME_REFERENCE].strip()
            if Const.PAYPAL_PREFIX in row[Const.ROW_NAME_USE] or Const.ALT_PAYPAL_SUFFIX in row[
                Const.ROW_NAME_REFERENCE] or Const.ALT_PAYPAL_SUFFIX in row[
                Const.ROW_NAME_RECIPIENT] or Const.PAYPAL_SUFFIX in row[Const.ROW_NAME_RECIPIENT]:
                match_ref_data = re.match(r'^(\S*).*$', row[Const.ROW_NAME_REFERENCE])
                if match_ref_data:
                    group_data = match_ref_data.groups()
                    code = group_data[0].strip()
            # elif ('AMZN Mktp DE' in row[Const.ROW_NAME_USE] or 'Amazon.de' in row[Const.ROW_NAME_USE]) and ('AMAZON PAYMENTS' in row[Const.ROW_NAME_RECIPIENT] or 'AMAZON EU' in row[Const.ROW_NAME_RECIPIENT]):
            #    match_data = re.match(
            #        r"^([0-9\-]+)\s+(AMZN Mktp DE|Amazon.de|Amazon.com|Amazon .Mktplce)\s+(\S+)\s*$", row[Const.ROW_NAME_USE])
            #    if match_data:
            #        group_data = match_data.groups()
            #        order = group_data[0]
            #        ref = group_data[2]
            #        code = "{}/{}".format(order, ref)
            elif re.match(r'^ZAHLBELEG\s*.*$', row[Const.ROW_NAME_REFERENCE]):
                code = row[Const.ROW_NAME_REFERENCE].replace('ZAHLBELEG ', '').strip()
            if not code:
                row_date = datetime.strptime(row[Const.ROW_NAME_BOOKING_DATE], '%d.%m.%y')
                if row_date:
                    code = "{}.{:04}".format(row_date.strftime('%Y-%m'), r)

            if code:
                out_row['code'] = code
                add_code_field = True
            out_row['payee'] = row[Const.ROW_NAME_RECIPIENT].replace(',', '').replace('\n', ' ')
            out_rows.append(out_row)
            r = r + 1
        utils.print_verbose("read csv: {}".format(filename_csv))

    with open(output_filename_csv, 'w', newline='') as out_csv_file:
        if add_code_field:
            headers.append('code')
        headers.append('payee')
        writer = csv.DictWriter(out_csv_file, fieldnames=headers, delimiter=Const.CSV_DELIMITER,
                                quotechar=Const.CSV_QUOTECHAR)
        writer.writeheader()
        for row in out_rows:
            writer.writerow(row)
        utils.print_verbose("write csv: {}".format(output_filename_csv))

    return out_rows


def clean_up_month_csv(config, year, month):
    src_year_dir = os.path.join(Const.SOURCE_PATH, "{}".format(year))
    src_month_dir = os.path.join(src_year_dir, "{:04}-{:02}".format(year, month))
    src_month_csv_dir = os.path.join(src_month_dir, 'csv')

    input_year_dir = os.path.join(Const.INPUT_PATH, "{}".format(year))
    input_month_dir = os.path.join(input_year_dir, "{:04}-{:02}".format(year, month))

    # if not os.path.exists(input_year_dir):
    #  os.mkdir(input_year_dir)
    # if not os.path.exists(input_month_dir):
    #  os.mkdir(input_month_dir)

    input_csv_filename = os.path.join(input_month_dir, "{:04}-{:02}.bank.csv".format(year, month))
    csv_filename = os.path.join(src_month_csv_dir, "{:04}-{:02}.bank.csv".format(year, month))

    if os.path.exists(input_csv_filename):
        if not os.path.exists(src_year_dir):
            os.mkdir(src_year_dir)
        if not os.path.exists(src_month_dir):
            os.mkdir(src_month_dir)
        if not os.path.exists(src_month_csv_dir):
            os.mkdir(src_month_csv_dir)
        clean_up_input_csv(input_csv_filename, csv_filename)
        utils.print_succ("write clean up csv: {} -> {}".format(input_csv_filename, csv_filename))
    else:
        utils.print_warn("{} not found".format(input_csv_filename))
