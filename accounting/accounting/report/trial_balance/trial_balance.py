# Copyright (c) 2013, gvn and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, _dict
import functools
from frappe.utils import getdate, flt

value_fields = ("opening_debit", "opening_credit", "debit",
                "credit", "closing_debit", "closing_credit")


def execute(filters=None):
    if filters.from_date > filters.to_date:
        frappe.throw(_("From Date cannot be greater than To Date"))

    data = get_data(filters)
    columns = get_columns()

    return columns, data


def filter_accounts(accounts, depth=10):
    parent_children_map = {}
    accounts_by_name = {}
    filtered_accounts = []

    for d in accounts:
        accounts_by_name[d.name] = d
        parent_children_map.setdefault(d.parent_account or None, []).append(d)

    def add_to_list(parent, level):
        if level < depth:
            children = parent_children_map.get(parent) or []
            children.sort(key=functools.cmp_to_key(cmp))

            for child in children:
                child.indent = level
                filtered_accounts.append(child)
                add_to_list(child.name, level + 1)

    add_to_list(None, -1)

    return filtered_accounts, accounts_by_name, parent_children_map


def get_opening_balances(filters):
    opening = frappe._dict()

    gle = frappe.db.sql("""
        select
            account, sum(debit) as opening_debit, sum(credit) as opening_credit
        from `tabGL Entry`
        where
           (DATE(posting_datetime) < %(from_date)s)
        group by account""",
        {
            "from_date": filters.from_date,
        },
        as_dict=True)

    for d in gle:
        opening.setdefault(d.account, d)

    return opening


def set_gl_entries_by_account(from_date, to_date, root_lft, root_rgt, filters):
    """Returns a dict like { "account": [gl entries], ... }"""
    gl_entries_by_account = {}

    accounts = frappe.db.sql_list("""select name from `tabAccount`
        where lft >= %s and rgt <= %s""", (root_lft, root_rgt))

    gl_filters = {
        "from_date": from_date,
        "to_date": to_date,
    }
    for key, value in filters.items():
        if value:
            gl_filters.update({
                key: value
            })
    gl_entries = frappe.db.sql(
        """
        select 
            posting_datetime, account, debit, credit 
        from `tabGL Entry`
        where 
            account in ({}) 
            and DATE(posting_datetime) <= %(to_date)s
        order by 
            account, DATE(posting_datetime)
        """.format(", ".join([frappe.db.escape(d) for d in accounts])), gl_filters, as_dict=True)

    for entry in gl_entries:
        gl_entries_by_account.setdefault(entry.account, []).append(entry)

    return gl_entries_by_account


def calculate_values(accounts, gl_entries_by_account, opening_balances, filters):
    init = {
        "opening_debit": 0.0,
        "opening_credit": 0.0,
        "debit": 0.0,
        "credit": 0.0,
        "closing_debit": 0.0,
        "closing_credit": 0.0
    }

    total_row = {
        "account": "'" + _("Total") + "'",
        "account_name": "'" + _("Total") + "'",
        "warn_if_negative": True,
        "opening_debit": 0.0,
        "opening_credit": 0.0,
        "debit": 0.0,
        "credit": 0.0,
        "closing_debit": 0.0,
        "closing_credit": 0.0,
        "parent_account": None,
        "indent": 0,
        "has_value": True,
    }

    for d in accounts:
        d.update(init.copy())

        d["opening_debit"] = opening_balances.get(
            d.name, {}).get("opening_debit", 0)
        d["opening_credit"] = opening_balances.get(
            d.name, {}).get("opening_credit", 0)

        for entry in gl_entries_by_account.get(d.name, []):
            d["debit"] += flt(entry.debit)
            d["credit"] += flt(entry.credit)

        some_value = flt(d["debit"]) - flt(d["credit"])
        if some_value > 0:
            d["closing_debit"] += abs(some_value)
        else:
            d["closing_credit"] += abs(some_value)
            

        total_row["debit"] += d["debit"]
        total_row["credit"] += d["credit"]

    return total_row


def accumulate_values_into_parents(accounts, accounts_by_name):
    for d in reversed(accounts):
        if d.parent_account:
            for key in value_fields:
                accounts_by_name[d.parent_account][key] += d[key]
    
    return accounts


def prepare_data(accounts, filters, total_row, parent_children_map):
    data = []
    for d in accounts:
        row = {
            "account": d.name,
            "parent_account": d.parent_account,
            "indent": d.indent,
            "from_date": filters.from_date,
            "to_date": filters.to_date,
            "account_name": d.account_name
        }

        d["closing_debit"] += d["opening_debit"]
        d["closing_credit"] += d["opening_credit"]

        for key in value_fields:
            row[key] = d.get(key, 0.0)

        data.append(row)
    
    data += [{}, total_row]
    
    return data[1:]


def get_data(filters):
    if filters.fiscal_year:
        fiscal_year = frappe.get_doc('Fiscal Year', filters.fiscal_year)
        filters.from_date, filters.to_date = str(fiscal_year.year_start_date), str(fiscal_year.year_end_date)
        
    accounts = frappe.db.sql(
        """ select 
                name, account_number, parent_account, account_name, lft, rgt
            from `tabAccount` 
            {}
            order by lft
        """.format("where account_name = '{}'".format(filters.account) if filters.account else ' ')
        , as_dict=True)

    min_lft, max_rgt = frappe.db.sql(
        r"select min(lft), max(rgt) from `tabAccount`")[0]
    accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)

    opening_balances = get_opening_balances(filters)

    gl_entries_by_account = set_gl_entries_by_account(filters.from_date, filters.to_date,
                              min_lft, max_rgt, filters)
    
    total_row = calculate_values(accounts, gl_entries_by_account, opening_balances, filters)
    
    accounts = accumulate_values_into_parents(accounts, accounts_by_name)

    data = prepare_data(accounts, filters, total_row, parent_children_map)
    
    return data


def get_columns():
    return [
        {
            "fieldname": "account",
            "label": _("Account"),
            "fieldtype": "Link",
            "options": "Account",
            "width": 300
        },
        {
            "fieldname": "opening_debit",
            "label": _("Opening (Dr)"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        },
        {
            "fieldname": "opening_credit",
            "label": _("Opening (Cr)"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        },
        {
            "fieldname": "debit",
            "label": _("Debit"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        },
        {
            "fieldname": "credit",
            "label": _("Credit"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        },
        {
            "fieldname": "closing_debit",
            "label": _("Closing (Dr)"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        },
        {
            "fieldname": "closing_credit",
            "label": _("Closing (Cr)"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        }
    ]
