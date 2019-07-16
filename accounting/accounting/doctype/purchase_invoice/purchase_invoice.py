# -*- coding: utf-8 -*-
# Copyright (c) 2019, gvn and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class PurchaseInvoice(Document):
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
        #  pay money: debit account
        doc = frappe.get_doc({
            'doctype': 'GL Entry',
            'posting_datetime': self.posting_timestamp,
            'voucher_type': self.doctype,
            'reference_doc': self.name,

            'account': self.assets_account,
            'debit': self.total_amount,
            'against_account': self.credit_to
        })
        doc.insert()

        # altering goods transaction: add to asset account
        doc = frappe.get_doc({
            'doctype': 'GL Entry',
            'posting_datetime': self.posting_timestamp,
            'voucher_type': self.doctype,
            'reference_doc': self.name,

            'account': self.credit_to,
            'credit': self.total_amount,
            'against_account': self.assets_account
        })
        doc.insert()

    def on_cancel(self):
        # reverse transactions
        # add more gl entries
        doc = frappe.get_doc({
            'doctype': 'GL Entry',
            'posting_datetime': now_datetime(),
            'voucher_type': self.doctype,
            'reference_doc': self.name,

            'account': self.credit_to,
            'debit': self.total_amount,
            'against_account': self.assets_account
        })
        doc.insert()

        #  pay money: debit account
        doc = frappe.get_doc({
            'doctype': 'GL Entry',
            'posting_datetime': now_datetime(),
            'voucher_type': self.doctype,
            'reference_doc': self.name,

            'account': self.assets_account,
            'credit': self.total_amount,
            'against_account': self.credit_to
        })
        doc.insert()
