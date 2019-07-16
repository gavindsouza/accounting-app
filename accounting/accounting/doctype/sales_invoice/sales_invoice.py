# -*- coding: utf-8 -*-
# Copyright (c) 2019, gvn and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


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
        #  get money: debit account
        doc = frappe.get_doc({
            'doctype': 'GL Entry',
            'posting_datetime': self.posting_timestamp,
            'voucher_type': self.doctype,
            'reference_doc': self.name,

            'against_account': self.assets_account,
            'account': self.debit_to,
            'debit': self.total_amount
        })
        doc.insert()

        # altering goods transaction: remove from asset account
        doc = frappe.get_doc({
            'doctype': 'GL Entry',
            'posting_datetime': self.posting_timestamp,
            'voucher_type': self.doctype,
            'reference_doc': self.name,

            'against_account': self.debit_to,
            'account': self.assets_account,
            'credit': self.total_amount
        })
        doc.insert()

    def on_cancel(self):
        # reverse transactions
        # altering goods transaction: insert to asset account
        doc = frappe.get_doc({
            'doctype': 'GL Entry',
            'posting_datetime': now_datetime(),
            'voucher_type': self.doctype,
            'reference_doc': self.name,

            'against_account': self.debit_to,
            'account': self.assets_account,
            'debit': self.total_amount
        })
        doc.insert()

        #  remove money: debit account
        doc = frappe.get_doc({
            'doctype': 'GL Entry',
            'posting_datetime': now_datetime(),
            'voucher_type': self.doctype,
            'reference_doc': self.name,

            'against_account': self.assets_account,
            'account': self.debit_to,
            'credit': self.total_amount
        })
        doc.insert()
