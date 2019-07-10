# Copyright (c) 2013, gvn and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _, _dict
from frappe.utils import getdate, flt
import frappe


def execute(filters=None):
    if not filters:
        return [], []

    account_details = _dict()

    for acc in frappe.db.sql("select name, is_group from tabAccount", as_dict=1):
        account_details[acc.name] = acc

    # validations
    if filters.from_date > filters.to_date:
        frappe.throw(_("From Date must be before To Date"))

    columns = get_columns()
    data = get_data(filters, account_details)

    return columns, data


def get_gl_entries(filters):
    general_ledger_entries = frappe.db.sql(
        "select * from `tabGL Entry` {} order by posting_datetime".format(
            conditions(filters)),
        filters,
        as_dict=1
    )

    return general_ledger_entries


def conditions(filters):
    if filters.get("account"):
        lft, rgt = frappe.db.get_value(
            "Account", filters["account"], ["lft", "rgt"])
        conditions = "account in (select name from tabAccount where lft >= {} and rgt <= {})".format(
            lft, rgt)

    else:
        conditions = "posting_datetime >= %(from_date)s and posting_datetime <=%(to_date)s"

    return "where {}".format(conditions)


def get_data_with_opening_closing(filters, account_details, gl_entries):
    gle_map = _dict()
    totals, entries = get_accountwise_gle(filters, gl_entries, gle_map)
    data = [totals.opening] + entries + [totals.total] + [totals.closing]

    def _get_balance(row, balance, debit_field, credit_field):
        balance += (row.get(debit_field, 0) - row.get(credit_field, 0))
        return balance

    for data_row in data:
        data_row['against'] = data_row.get('against_account')

        if not data_row.get('posting_datetime'):
            balance = 0

        balance = _get_balance(data_row, balance, 'debit', 'credit')
        data_row['balance'] = balance

    return data


def get_accountwise_gle(filters, general_ledger_entries, gle_map):
    from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
    totals = get_totals()
    entries = []

    def _update_value_in_dict(data, key, gle):
        data[key].debit += flt(gle.debit)
        data[key].credit += flt(gle.credit)

    for gle in general_ledger_entries:
        if gle.posting_datetime.date() < from_date:
            _update_value_in_dict(totals, 'opening', gle)
            _update_value_in_dict(totals, 'closing', gle)

        elif gle.posting_datetime.date() <= to_date:
            _update_value_in_dict(totals, 'total', gle)
            _update_value_in_dict(totals, 'closing', gle)
            entries += [gle]

    return totals, entries


def get_totals():
    def _get_debit_credit_dict(label):
        return _dict(
            account="'{0}'".format(label),
            debit=0.0,
            credit=0.0
        )

    return _dict(
        opening=_get_debit_credit_dict(_('Opening')),
        total=_get_debit_credit_dict(_('Total')),
        closing=_get_debit_credit_dict(_('Closing (Opening + Total)'))
    )


def get_data(filters, account_details):
    general_ledger_entries = get_gl_entries(filters)
    data = get_data_with_opening_closing(
        filters, account_details, general_ledger_entries)

    return data


def get_columns():
    columns = [
        {
            "label": _("Reference Doc"),
            "fieldname": "reference_doc",
            "fieldtype": "Dynamic Link",
            "width": 90
        },
        {
            "label": _("Posting Timestamp"),
            "fieldname": "posting_datetime",
            "fieldtype": "Date",
            "width": 90
        },
        {
            "label": _("Account"),
            "fieldname": "account",
            "fieldtype": "Link",
            "options": "Account",
            "width": 180
        },
        {
            "label": _("Debit (INR)"),
            "fieldname": "debit",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Credit (INR)"),
            "fieldname": "credit",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Balance (INR)"),
            "fieldname": "balance",
            "fieldtype": "Float",
            "width": 130
        },
        {
            "label": _("Transaction Type"),
            "fieldname": "transaction_type",
            "width": 120
        },
        {
            "label": _("Against Account"),
            "fieldname": "against_account",
            "width": 120
        },
        {
            "label": _("Party"),
            "fieldname": "party",
            "fieldtype": "Link",
            "options": "Party",
            "width": 100
        }
    ]

    return columns
