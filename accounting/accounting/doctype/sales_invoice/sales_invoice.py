# -*- coding: utf-8 -*-
# Copyright (c) 2019, gvn and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document


class SalesInvoice(Document):
    def validate(self):
        items = self.get('items')
        for item in items:
            if item.item_quantity < 0:
                frappe.throw(_("Item quantity cannot be negative"))
            if item.item_rate <= 0:
                frappe.throw(_("Item rate must be non zero"))
            if item.item_amount == 0:
                frappe.throw(_("Amount cannot be zero"))

    def on_submit(self):
        # altering goods transaction: remove from asset account
        doc = frappe.get_doc({
            'doctype': 'GL Entry',
            'posting_datetime': self.posting_timestamp,
            'account': self.assets_account,
            'credit': self.total_amount,
            'voucher_type': self.doctype,
            'against_account': self.debit_to,
            'reference_doc': self.name
        })
        doc.insert()

        doc = frappe.get_doc("Account", self.assets_account)
        doc.account_balance = doc.account_balance - float(self.total_amount)
        doc.save()

        #  get money: debit account
        doc = frappe.get_doc({
            'doctype': 'GL Entry',
            'posting_datetime': self.posting_timestamp,
            'account': self.debit_to,
            'debit': self.total_amount,
            'voucher_type': self.doctype,
            'against_account': self.assets_account,
            'reference_doc': self.name
        })
        doc.insert()

        doc = frappe.get_doc("Account", self.debit_to)
        doc.account_balance = doc.account_balance + float(self.total_amount)
        doc.save()

    def on_cancel(self):
        # reverse transactions
        doc = frappe.get_doc("Account", self.assets_account)
        doc.account_balance = doc.account_balance + float(self.total_amount)
        doc.save()

        doc = frappe.get_doc("Account", self.debit_to)
        doc.account_balance = doc.account_balance - float(self.total_amount)
        doc.save()

        # remove gl entry
        frappe.db.sql("""
            delete from `tabGL Entry` 
            where reference_doc={} 
        """.format(self.name))
