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
        # decision_rules = {
        #     'Sales Invoice': {'submit': self.make_sales_entry(), 'cancel': self.reverse_sales_entry()},
        #     'Purchase Invoice': {'submit': self.make_purchase_entry(), 'cancel': self.reverse_purchase_entry()}
        # }
        # decision_rules[self.transaction_type][_type]

        if self.transaction_type == "Sales Invoice":
            if _type == 'submit':
                self.make_sales_entry()
            elif _type == 'cancel':
                self.reverse_sales_entry()

        elif self.transaction_type == "Purchase Invoice":
            if _type == 'submit':
                self.make_purchase_entry()
            elif _type == 'cancel':
                self.reverse_purchase_entry()

        else:
            frappe.throw(_("Invalid operation in {}".format(self.doctype)))

    def make_sales_entry(self):
        # transfer funds
        doc = self.base_doc()
        doc.account = self.paid_to
        doc.against_account = self.party
        doc.debit = self.payment_amount
        doc.reason = "Transfer of funds to {}: {} against {} on {}".format(
            self.party, self.doctype, self.transaction_type, getdate(self.posting_timestamp))
        doc.insert()

        # transfer goods
        doc = self.base_doc()
        doc.account = self.paid_from
        doc.against_account = self.party
        doc.credit = self.payment_amount
        doc.reason = "Update {} from {}: {} against {} on {}".format(
            self.paid_from, self.party, self.doctype, self.transaction_type, getdate(self.posting_timestamp))
        doc.insert()

    def reverse_sales_entry(self):
        # reverse: transfer goods
        doc = self.base_doc()
        doc.account = self.paid_from
        doc.against_account = self.party
        doc.posting_datetime = now_datetime()
        doc.debit = self.payment_amount
        doc.reason = "Cancelled Transaction on {}".format(
            getdate(doc.posting_datetime))
        doc.insert()

        # reverse: transfer funds
        doc = self.base_doc()
        doc.account = self.paid_to
        doc.against_account = self.party
        doc.posting_datetime = now_datetime()
        doc.credit = self.payment_amount
        doc.reason = "Cancelled Transaction on {}".format(
            getdate(doc.posting_datetime))
        doc.insert()

    def make_purchase_entry(self):
        # transfer goods
        doc = self.base_doc()
        doc.account = self.paid_to
        doc.against_account = self.paid_from
        doc.debit = self.payment_amount
        doc.reason = "Update {} from {}: {} against {} on {}".format(
            self.paid_to, self.paid_from, self.doctype, self.transaction_type, getdate(self.posting_timestamp))
        doc.insert()

        # transfer funds
        doc = self.base_doc()
        doc.account = self.paid_from
        doc.against_account = self.party
        doc.credit = self.payment_amount
        doc.reason = "Transfer of funds from {}: {} against {} on {}".format(
            self.paid_from, self.doctype, self.transaction_type, getdate(self.posting_timestamp))
        doc.insert()

    def reverse_purchase_entry(self):
        # reverse: transfer funds
        doc = self.base_doc()
        doc.account = self.paid_from
        doc.against_account = self.party
        doc.posting_datetime = now_datetime()
        doc.debit = self.payment_amount
        doc.reason = "Cancelled Transaction on {}".format(
            getdate(doc.posting_datetime))
        doc.insert()

        # reverse: transfer goods
        doc = self.base_doc()
        doc.account = self.paid_to
        doc.against_account = self.paid_from
        doc.posting_datetime = now_datetime()
        doc.credit = self.payment_amount
        doc.reason = "Cancelled Transaction on {}".format(
            getdate(doc.posting_datetime))
        doc.insert()

    def base_doc(self):
        doc = frappe.get_doc({
            'doctype': 'GL Entry',
            'posting_datetime': self.posting_timestamp,
            'voucher_type': self.doctype,
        })
        doc.reference_doc = self.name
        return doc
