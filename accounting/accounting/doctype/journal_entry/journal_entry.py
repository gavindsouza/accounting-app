# -*- coding: utf-8 -*-
# Copyright (c) 2019, gvn and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.nestedset import get_descendants_of


class JournalEntry(Document):
    def validate(self):
        journal_entries = self.get('journal_entry_table')
        total_debit = self.get('total_debit')
        total_credit = self.get('total_credit')

        for entry in journal_entries:
            if (entry.debit < 0 and entry.credit < 0) or (entry.debit > 0 and entry.credit > 0):
                frappe.throw(_("Something's off"))

        if total_credit != total_debit:
            frappe.throw(_("Total Debit and Total Credit must be equal: {} != {}".format(
                total_debit, total_credit)))

        if len(journal_entries) < 2:
            frappe.throw(_("Entry's Missing?"))

        if set(x for x in entry.account) < len(journal_entries):
            frappe.throw(_("Can't have the same account twice like that fam"))

    def on_submit(self):
        self.update_accounts_balance()
        self.make_gl_entry()

    def update_accounts_balance(self):
        # Assets = get_descendants_of('Account', 'Assets')
        # Expenses = get_descendants_of('Account', 'Expenses')
        # Income = get_descendants_of('Account', 'Income')
        # Liabilities = get_descendants_of('Account', 'Liabilities')

        Assets = ['Debtors', 'Stock in Hand']
        Expenses = []
        Income = ['Cost of Goods Sold']
        Liabilities = ['Creditors']

        for entry in self.get("journal_entry_table"):
            doc = frappe.get_doc("Account", entry.account)
            if doc.root_type in Assets + Expenses:
                if entry.debit > 0:
                    doc.balance += entry.debit
                elif entry.credit > 0:
                    doc.balance -= entry.credit

            elif doc.root_type in Income + Liabilities:
                if entry.debit > 0:
                    doc.balance -= entry.debit
                elif entry.credit > 0:
                    doc.balance += entry.credit

            doc.save()


    def make_gl_entry(self):
        
        if hasattr(self, 'against_account'):
            pass
        else: 
            self.against_account = ''

        for entry in self.get('journal_entry_table'):
            doc = frappe.get_doc({
                'doctype': 'GL Entry',
                'posting_datetime': self.posting_timestamp,
                'account': entry.account,
                'party': entry.party,
                'debit': entry.debit,
                'credit': entry.credit,
                'against_account': self.against_account,
                'voucher_type': self.doctype,
                'reason': entry.reason
            })
            doc.insert()