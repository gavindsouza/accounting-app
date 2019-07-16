# -*- coding: utf-8 -*-
# Copyright (c) 2019, gvn and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, flt, now_datetime
from frappe.model.document import Document


class PaymentEntry(Document):
    def validate(self):
        existing_payment_entry = frappe.db.exists({
            'doctype': 'Payment Entry',
            'docstatus': '<2',
            'reference_invoice': self.reference_invoice
        })

        if len(existing_payment_entry) > 1:
            frappe.throw(_("Payment Entry {} exists".format(
                existing_payment_entry[0][0])))

    def on_submit(self):
        self.make_gl_entry(_type='submit')

    def on_cancel(self):
        self.make_gl_entry(_type='cancel')

    def make_gl_entry(self, _type):
        doc = frappe.get_doc({
            'doctype': 'GL Entry',
            'posting_datetime': self.posting_timestamp,
            'voucher_type': self.doctype,
            'reference_doc': self.reference_invoice
        })

        if self.transaction_type == "Sales Invoice":
            doc.account = self.paid_to
            doc.against_account = self.party

            if _type == "submit":
                doc.debit = self.payment_amount
                doc.reason = "Transfer of funds from {}: {} against {} on {}".format(
                    self.party, self.doctype, self.transaction_type, getdate(self.posting_timestamp))

            elif _type == "cancel":
                doc.posting_datetime = now_datetime()
                doc.credit = self.payment_amount
                doc.reason = "Cancelled"

            doc.insert()

            doc = frappe.get_doc({
                'doctype': 'GL Entry',
                'posting_datetime': self.posting_timestamp,
                'voucher_type': self.doctype,
                'reference_doc': self.reference_invoice
            })
            doc.account = self.paid_from
            doc.against_account = self.against_account

            if _type == "submit":
                doc.credit = self.payment_amount
                doc.debit = None
                doc.reason = "Update {} from {}: {} against {} on {}".format(
                    self.paid_from, self.against_account, self.doctype, self.transaction_type, getdate(self.posting_timestamp))

            elif _type == "cancel":
                doc.posting_datetime = now_datetime()
                doc.debit = self.payment_amount
                doc.credit = None
                doc.reason = "Cancelled"
            doc.insert()

        elif self.transaction_type == "Purchase Invoice":
            doc.account = self.paid_from
            doc.against_account = self.party

            if _type == "submit":
                doc.credit = self.payment_amount
                doc.debit = None
                doc.reason = "Transfer of funds from {}: {} against {} on {}".format(
                    self.paid_from, self.doctype, self.transaction_type, getdate(self.posting_timestamp))

            elif _type == "cancel":
                doc.posting_datetime = now_datetime()
                doc.credit = None
                doc.debit = self.payment_amount
                doc.reason = "Cancelled"

            doc.insert()

            doc = frappe.get_doc({
                'doctype': 'GL Entry',
                'posting_datetime': self.posting_timestamp,
                'voucher_type': self.doctype,
                'reference_doc': self.reference_invoice
            })
            doc.account = self.paid_to
            doc.against_account = self.paid_from

            if _type == 'submit':
                doc.debit = self.payment_amount
                doc.credit = None
                doc.reason = "Update {} from {}: {} against {} on {}".format(
                    self.paid_to, self.paid_from, self.doctype, self.transaction_type, getdate(self.posting_timestamp))

            elif _type == "cancel":
                doc.posting_datetime = now_datetime()
                doc.credit = self.payment_amount
                doc.debit = None
                doc.reason = "Cancelled"

            doc.insert()

        else:
            frappe.throw(_("Invalid operation in {}".format(self.doctype)))
