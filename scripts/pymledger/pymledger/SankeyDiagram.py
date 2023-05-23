import plotly.graph_objects as go

from pymledger import Const, utils
from pymledger.HledgerUtils import string_to_amount_value


def get_sankey_row_cols(config, row):
    ret = []
    cols = row['account'].split(':')
    for col_length in range(len(cols)):
        ret.append(':'.join(cols[:col_length + 1]))
    return [x for x in ret if x != '']


def get_sankey_rows_cols(config, rows):
    ret = set()
    for row in rows:
        if row['account'] != 'total':
            ret = ret.union(set(get_sankey_row_cols(config, row)))
    return sorted(list(ret))


def get_sankey_rows_values(config, rows):
    ret = {}
    cols = get_sankey_rows_cols(config, rows)
    for row in rows:
        for col in cols:
            if row['account'].startswith(col):
                amount = row[sorted(row.keys())[-1]].replace(Const.CURRENCY, '').replace(' ', '')
                if col not in ret:
                    ret[col] = 0.0
                ret[col] = ret[col] + string_to_amount_value(amount)
    return ret


def get_sankey_label(config, source_label, rows):
    label = [source_label]
    label.extend(get_sankey_rows_cols(config, rows))
    return label


def get_sankey_link(config, source_label, rows):
    values = get_sankey_rows_values(config, rows)
    label = get_sankey_label(config, source_label, rows)
    source = []
    target = []
    value = []
    for row in rows:
        if row['account'] != 'total':
            source.append(0)
            target.append(label.index(row['account']))
            value.append(values[row['account']])

    return {'source': source, 'target': target, 'value': value}


def get_sankey_data(config, source_label, rows):
    label = get_sankey_label(config, source_label, rows)
    link = get_sankey_link(config, source_label, rows)
    return get_sankey_go_data(config, label, link)


def get_sankey_go_data(config, label, link):
    label = [Const.ACCOUNTS_TITLE[l] if l in Const.ACCOUNTS_TITLE else l for l in label]
    ret = {'node': {'label': label}, 'link': link}

    if 'sankey' in config and 'node' in config['sankey']:
        if 'pad' in config['sankey']['node']:
            ret['node']['pad'] = config['sankey']['node']['pad']
        if 'thickness' in config['sankey']['node']:
            ret['node']['thickness'] = config['sankey']['node']['thickness']
        if 'line' in config['sankey']['node']:
            ret['node']['line'] = config['sankey']['node']['line']
        if 'line' in config['sankey']['node']:
            ret['node']['color'] = config['sankey']['node']['color']

    if 'sankey' in config and 'label_aliases' in config['sankey']:
        i = 0
        for label_value in ret['node']['label']:
            if label_value in config['sankey']['label_aliases']:
                ret['node']['label'][i] = config['sankey']['label_aliases']
            i = i + 1

    ret['valueformat'] = ".2f {}".format(Const.CURRENCY)
    ret['valuesuffix'] = " {}".format(Const.CURRENCY)

    # utils.print_debug(ret)

    return ret


def get_sankey_data_budget_expenses_link_data(config, label, unbudget_label, budget_label, expenses_label, budget_rows,
                                              expenses_rows, depth=None):
    budget_values = get_sankey_rows_values(config, budget_rows)
    expenses_values = get_sankey_rows_values(config, expenses_rows)

    source = []
    target = []
    value = []
    customdata = []

    total_budget_value = round(budget_values[budget_label], 2)
    total_expenses_value = round(expenses_values[expenses_label], 2)

    for budget_row in budget_rows:
        budget_account = budget_row['account']
        budget_account_depth = len([c for c in budget_account if c == ':']) + 1
        # utils.print_debug(budget_account)
        if (budget_account.startswith(
                budget_label) and budget_account != budget_label and budget_account != 'total') and (
                not depth or budget_account_depth <= depth):
            budget_value = round(budget_values[budget_row['account']], 2)

            source.append(label.index(budget_label))
            target.append(label.index(budget_row['account']))
            value.append(budget_value)

            budget_value_percent = budget_value / total_budget_value * 100
            customdata.append("{:.2f}%".format(budget_value_percent))

            budget_expense = Const.FORECAST_BUDGET_EXPENSE_MAP[budget_row['account']]
            # utils.print_debug(budget_row['account'])
            # utils.print_debug(budget_expense)
            for expenses_row in expenses_rows:
                expenses_account = expenses_row['account']
                expenses_account_depth = len([c for c in expenses_account if c == ':']) + 1
                if (expenses_account == budget_expense and expenses_account != 'total') and (
                        not depth or expenses_account_depth <= depth):
                    expenses_value = round(expenses_values[expenses_row['account']], 2)

                    source.append(label.index(budget_row['account']))
                    target.append(label.index(budget_expense))
                    value.append(expenses_value)

                    expenses_value_percent = expenses_value / budget_value * 100
                    customdata.append("{:.2f}%".format(expenses_value_percent))

                    if ('sankey' in config and 'show_unbudget' in config['sankey'] and config['sankey'][
                        'show_unbudget']) and (not depth or unbudget_label <= depth):
                        unbudget_value = budget_value - expenses_value
                        unbudget_value_percent = unbudget_value / budget_value * 100
                        if unbudget_value > 0:
                            source.append(label.index(budget_row['account']))
                            target.append(label.index(unbudget_label))
                            value.append(unbudget_value)
                            customdata.append("{:.2f}%".format(unbudget_value_percent))

    for expenses_row in expenses_rows:
        expenses_account = expenses_row['account']
        expenses_account_depth = len([c for c in expenses_account if c == ':']) + 1
        if (expenses_account.startswith(expenses_label) and expenses_account != 'total') and (
                not depth or expenses_account_depth <= depth):
            expenses_value = expenses_values[expenses_row['account']]

            source.append(label.index(expenses_row['account']))
            target.append(label.index(expenses_label))
            value.append(expenses_value)

            expenses_value_percent = expenses_value / total_expenses_value * 100
            customdata.append("{:.2f}%".format(expenses_value_percent))

    return source, target, value, customdata


def get_sankey_data_budget_expenses(config, unbudget_label, budget_label, expenses_label, budget_rows, expenses_rows,
                                    depth=None):
    label = set()
    label = label.union(get_sankey_label(config, budget_label, budget_rows))
    label = label.union(get_sankey_label(config, expenses_label, expenses_rows))
    label = label.union(Const.FORECAST_BUDGET_EXPENSE_MAP.values())
    label = sorted(list(label))
    if unbudget_label and 'sankey' in config and 'show_unbudget' in config['sankey'] and config['sankey'][
        'show_unbudget']:
        label.append(unbudget_label)

    source, target, value, customdata = get_sankey_data_budget_expenses_link_data(config, label, unbudget_label,
                                                                                  budget_label, expenses_label,
                                                                                  budget_rows, expenses_rows, depth)

    link = {'source': source, 'target': target, 'value': value, 'customdata': customdata,
            'hovertemplate': "%{source.label} -> %{target.label}: %{value} (%{customdata})<extra></extra>"}

    return get_sankey_go_data(config, label, link)


def get_sankey_data_income_budget(config, income_label, income_rows, budget_label, depth=None):
    label = set()
    label = label.union(get_sankey_label(config, income_label, income_rows))
    label = label.union(Const.FORECAST_BUDGET_EXPENSE_MAP.values())
    label = sorted(list(label))
    label.append(budget_label)

    income_values = get_sankey_rows_values(config, income_rows)

    total_income_value = round(income_values[income_label], 2)

    source = []
    target = []
    value = []
    customdata = []

    for income_row in income_rows:
        income_account = income_row['account']
        income_account_depth = len([c for c in income_account if c == ':']) + 1
        if (income_account.startswith(income_label) and income_account != 'total') and (
                not depth or income_account_depth <= depth):
            income_value = round(income_values[income_row['account']], 2)

            source.append(label.index(income_row['account']))
            target.append(label.index(budget_label))
            value.append(abs(income_value))

            # TODO: add function for make customdata from value
            income_value_percent = income_value / total_income_value * 100
            customdata.append("{:.2f}%".format(abs(income_value_percent)))

    link = {'source': source, 'target': target, 'value': value, 'customdata': customdata,
            'hovertemplate': "%{source.label} -> %{target.label}: %{value} (%{customdata})<extra></extra>"}

    utils.print_debug(link)

    return get_sankey_go_data(config, label, link)


def get_sankey_data_income_budget_expenses(config, income_label, income_rows, unbudget_label, budget_label,
                                           expenses_label, budget_rows, expenses_rows, depth=None):
    label = set()
    label = label.union(get_sankey_label(config, income_label, income_rows))
    label = label.union(get_sankey_label(config, budget_label, budget_rows))
    label = label.union(get_sankey_label(config, expenses_label, expenses_rows))
    label = label.union(Const.FORECAST_BUDGET_EXPENSE_MAP.values())
    label = sorted(list(label))
    if unbudget_label and 'sankey' in config and 'show_unbudget' in config['sankey'] and config['sankey'][
        'show_unbudget']:
        label.append(unbudget_label)

    income_values = get_sankey_rows_values(config, income_rows)

    total_income_value = round(income_values[income_label], 2)

    source, target, value, customdata = get_sankey_data_budget_expenses_link_data(config, label, unbudget_label,
                                                                                  budget_label, expenses_label,
                                                                                  budget_rows, expenses_rows, depth)

    for income_row in income_rows:
        income_account = income_row['account']
        income_account_depth = len([c for c in income_account if c == ':']) + 1
        if (income_account.startswith(income_label) and income_account != 'total') and (
                not depth or income_account_depth <= depth):
            income_value = round(income_values[income_row['account']], 2)

            source.append(label.index(income_row['account']))
            target.append(label.index(budget_label))
            value.append(abs(income_value))

            # TODO: add function for make customdata from value
            income_value_percent = income_value / total_income_value * 100
            customdata.append("{:.2f}%".format(abs(income_value_percent)))

    link = {'source': source, 'target': target, 'value': value, 'customdata': customdata,
            'hovertemplate': "%{source.label} -> %{target.label}: %{value} (%{customdata})<extra></extra>"}

    return get_sankey_go_data(config, label, link)


def get_sankey_data_income_budget_plotly_figure(config, income_label, income_rows, budget_label, depth=None):
    fig = go.Figure(data=[go.Sankey(
        get_sankey_data_income_budget(config, income_label, income_rows, budget_label, depth))])
    if 'sanky' in config and 'title_text' in config['sankey'] and 'font_size' in config['sankey']:
        fig.update_layout(title_text=config['sankey']['title_text'], font_size=config['sankey']['font_size'])
    return fig


def get_sankey_data_income_budget_expenses_plotly_figure(config, income_label, income_rows, unbudget_label,
                                                         budget_label, expenses_label, budget_rows, expenses_rows,
                                                         depth=None):
    fig = go.Figure(data=[go.Sankey(
        get_sankey_data_income_budget_expenses(config, income_label, income_rows, unbudget_label, budget_label,
                                               expenses_label, budget_rows, expenses_rows, depth))])
    if 'sanky' in config and 'title_text' in config['sankey'] and 'font_size' in config['sankey']:
        fig.update_layout(title_text=config['sankey']['title_text'], font_size=config['sankey']['font_size'])
    return fig


def get_sankey_data_budget_expenses_plotly_figure(config, unbudget_label, budget_label, expenses_label, budget_rows,
                                                  expenses_rows, depth=None):
    fig = go.Figure(data=[go.Sankey(
        get_sankey_data_budget_expenses(config, unbudget_label, budget_label, expenses_label, budget_rows,
                                        expenses_rows, depth))])
    if 'sanky' in config and 'title_text' in config['sankey'] and 'font_size' in config['sankey']:
        fig.update_layout(title_text=config['sankey']['title_text'], font_size=config['sankey']['font_size'])
    return fig


def get_sankey_data_budget_expenses_plot(filename, config, unbudget_label, budget_label, expenses_label, budget_rows,
                                         expenses_rows, depth=None):
    fig = get_sankey_data_budget_expenses_plotly_figure(config, unbudget_label, budget_label, expenses_label,
                                                        budget_rows, expenses_rows, depth)
    fig.write_image(filename)


def get_sankey_data_plotly_figure(config, source_label, rows):
    fig = go.Figure(data=[go.Sankey(get_sankey_data(config, source_label, rows))])
    if 'sanky' in config and 'title_text' in config['sankey'] and 'font_size' in config['sankey']:
        fig.update_layout(title_text=config['sankey']['title_text'], font_size=config['sankey']['font_size'])
    return fig


def get_sankey_data_plot(filename, config, source_label, rows, depth=None):
    fig = get_sankey_data_plotly_figure(config, source_label, rows, depth)
    fig.write_image(filename)
