# -*- coding: utf-8 -*-
# Copyright (c) 2019, gvn and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.nestedset import get_descendants_of
from operator import neg, pos
from frappe.utils import flt


class GLEntry(Document):
    def __init__(self, *args, **kwargs):
        super(GLEntry, self).__init__(*args, **kwargs)

        leaves = [x.name for x in frappe.get_list(
            'Account', filters={'is_group': 0})]
        self._assets = [x for x in get_descendants_of(
            'Account', 'Assets') if x in leaves]
        self._expenses = [x for x in get_descendants_of(
            'Account', 'Expenses') if x in leaves]
        self._income = [x for x in get_descendants_of(
            'Account', 'Income') if x in leaves]
        self._liabilities = [x for x in get_descendants_of(
            'Account', 'Liabilities') if x in leaves]

    def validate(self):
        self.account_doc = frappe.get_doc('Account',
                                          self.account)

        if self.account in self._assets + self._expenses:
            self.increase_with_debit()
        elif self.account in self._income + self._liabilities:
            self.increase_with_credit()

    def increase_with_debit(self):
        self.account_doc.account_balance += flt(self.debit)
        self.account_doc.account_balance -= flt(self.credit)
        self.account_doc.save()

    def increase_with_credit(self):
        self.account_doc.account_balance -= flt(self.debit)
        self.account_doc.account_balance += flt(self.credit)
        self.account_doc.save()

    # def update_balance(self, op):
    #     for acc in [self.account_doc.account_balance, self.against_account_doc.account_balance]:
    #         acc += op(flt(self.debit))
    #         acc -= op(flt(self.credit))
