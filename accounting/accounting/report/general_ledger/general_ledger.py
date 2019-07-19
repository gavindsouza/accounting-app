# Copyright (c) 2013, gvn and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _, _dict
from frappe.utils import getdate, flt
import frappe
from frappe.utils import datetime


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

    query = "select * from `tabGL Entry` {} order by posting_datetime".format(
            conditions(filters))
    print("query: " + query)
    general_ledger_entries = frappe.db.sql(query, filters, as_dict=1)

    return general_ledger_entries


def conditions(filters):
    voucher_type = filters.get('voucher_type')
    account = filters.get("account")
    reference_document = filters.get("reference_document")
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')

    conditions = []

    if not (to_date and from_date):
        from_date = datetime.MINYEAR
        to_date = datetime.datetime.today()
    
    if account:
        lft, rgt = frappe.db.get_value(
            "Account", filters["account"], ["lft", "rgt"])
        conditions += ["account in (select name from tabAccount where lft >= {} and rgt <= {})".format(
            lft, rgt)]
    if voucher_type:
        conditions += ["voucher_type='{}'".format(voucher_type)]
    if reference_document:
        conditions += ["reference_doc='{}'".format(reference_document)]

    # conditions += ["DATE(posting_datetime) >= '{}' and DATE(posting_datetime) <= '{}'".format(from_date, to_date)]
    where_conditions = "where {}".format(' and '.join(conditions))

    return where_conditions


def get_data_with_opening_closing(filters, account_details, gl_entries):
    gle_map = _dict()
    totals, entries = get_accountwise_gle(filters, gl_entries, gle_map)
    data = [totals.opening] + entries + [totals.total] + [totals.closing]

    def _get_balance(row, balance, debit_field, credit_field):
        balance += (row.get(debit_field, 0) - row.get(credit_field, 0))
        return balance

    for data_row in data:
        if not data_row.get('posting_datetime'):
            balance = 0

        data_row['balance'] = _get_balance(
            data_row, balance, 'debit', 'credit')

    return data


def get_accountwise_gle(filters, general_ledger_entries, gle_map):
    from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
    totals = get_totals()
    entries = []

    def _update_values(data, key, gle):
        data[key].debit += flt(gle.debit)
        data[key].credit += flt(gle.credit)

    for gle in general_ledger_entries:
        if gle.posting_datetime.date() < from_date:
            _update_values(totals, 'opening', gle)
            _update_values(totals, 'closing', gle)

        elif gle.posting_datetime.date() <= to_date:
            _update_values(totals, 'total', gle)
            _update_values(totals, 'closing', gle)
            entries += [gle]

    return totals, entries


def get_totals():
    def _get_debit_credit_dict(label):
        return _dict(
            account="'{0}'".format(label),
            debit=0,
            credit=0
        )

    return _dict(
        opening=_get_debit_credit_dict(_('Opening')),
        total=_get_debit_credit_dict(_('Total')),
        closing=_get_debit_credit_dict(_('Closing (Opening + Total)'))
    )


def get_data(filters, account_details):
    if not filters.get('account'):
        filters['account'] = 'Company Root'

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
            "options": "voucher_type",
            "width": 150
        },
        {
            "label": _("Posting Timestamp"),
            "fieldname": "posting_datetime",
            "fieldtype": "Date",
            "width": 150
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
            "label": _("Voucher Type"),
            "fieldname": "voucher_type",
            "fieldtype": "Link",
            "options": "DocType",
            "width": 120
        },
        {
            "label": _("Against Account"),
            "fieldname": "against_account",
            "width": 100
        },
        {
            "label": _("Reason"),
            "fieldname": "reason",
            "width": 250
        }
    ]

    return columns
