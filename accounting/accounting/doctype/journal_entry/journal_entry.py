# -*- coding: utf-8 -*-
# Copyright (c) 2019, gvn and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate
from frappe.model.document import Document
from frappe.utils import now_datetime


class JournalEntry(Document):
    def validate(self):
        journal_entries = self.get('journal_entry_table')
        total_debit = self.get('total_debit')
        total_credit = self.get('total_credit')
        accounts_in = []

        for entry in journal_entries:
            accounts_in.append(entry.account)
            if (entry.debit < 0 and entry.credit < 0) or (entry.debit > 0 and entry.credit > 0):
                frappe.throw(_("Something's off"))

        if total_credit != total_debit:
            frappe.throw(_("Total Debit and Total Credit must be equal: {} != {}".format(
                total_debit, total_credit)))

        if len(journal_entries) < 2:
            frappe.throw(_("Entry's Missing?"))

        if len(set(accounts_in)) < len(journal_entries):
            frappe.throw(_("Can't have the same account twice like that fam"))

    def on_submit(self):
        self.make_gl_entry(_type='submit')

    def on_cancel(self):
        self.make_gl_entry(_type='cancel')

    def make_gl_entry(self, _type):
        if hasattr(self, 'against_account'):
            pass
        else:
            self.against_account = ''

        for entry in self.get('journal_entry_table'):
            doc = frappe.get_doc({
                'doctype': 'GL Entry',
                'account': entry.account,
                'party': entry.party,
                'against_account': self.against_account,
                'voucher_type': self.doctype,
                'reference_doc': self.name
            })

            if _type == 'submit':
                doc.posting_datetime = self.posting_timestamp
                doc.debit = entry.debit
                doc.credit = entry.credit
                doc.reason = entry.reason

            elif _type == 'cancel':
                doc.posting_datetime = now_datetime()
                doc.credit = entry.debit
                doc.debit = entry.credit
                doc.reason = "Cancelled {} on {}".format(
                    self.doctype, getdate(doc.posting_datetime)) + entry.reason
            else:
                frappe.throw(_("Invalid journal entry type"))

            doc.insert()
