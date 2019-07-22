# -*- coding: utf-8 -*-
# Copyright (c) 2019, gvn and Contributors
# See license.txt

# imports - stndard imports
from __future__ import unicode_literals
import unittest

# imports - module imports
import frappe
from frappe.utils import now_datetime, flt
from accounting.accounting.doctype.account.test_account import create_accounts

test_dependencies = ['Party', 'Account', 'Item']


def add_pur_invoice():
	pur_invoice = frappe.get_doc({
		'doctype': 'Purchase Invoice',
		'party': 'test_party_001',
		'posting_timestamp': now_datetime(),
		'credit_to': 'Creditors',
		'assets_account': 'Stock in Hand',
		'items': [
			{
				'item': 'test_item_001',
				'item_quantity': 10,
				'item_rate': 1000,
			}
		],
		'total_amount': 10 * 1000
	})
	pur_invoice.submit()


class TestPurchaseInvoice(unittest.TestCase):
	def setUp(self):
		create_accounts()
		add_pur_invoice()

	def test_make_bad_purchase_invoice(self):
		doc = frappe.get_doc({
			'doctype': 'Purchase Invoice',
			'party': 'test_party_001',
			'posting_timestamp': now_datetime(),
			'items': [{
				'item': 'test_item_001',
				'item_quantity': 10,
				'item_rate': 1000,
			}]
		})

		self.assertRaises(frappe.MandatoryError, doc.submit)

	def test_cancel_purchase_invoice(self):
		for doc in frappe.get_all('Purchase Invoice'):
			if doc.docstatus == 1:
				doc.cancel()

	def test_make_payment_entry(self):
		pur_invoice = frappe.get_doc(
			'Purchase Invoice', 
			frappe.get_all('Purchase Invoice')[-1].name
		)
		# print(vars(pur_invoice))
		
		pay_entry = frappe.get_doc(dict(
			doctype='Payment Entry',
			transaction_type=pur_invoice.doctype,
			reference_invoice=pur_invoice.name,
			payment_amount=500000
		)).insert()

		# amount will be reset to the bill amount since is greater
		self.assertEqual(flt(pay_entry.payment_amount), 10000)

	def test_make_another_payment_entry(self):
		add_pur_invoice()

		pur_invoice = frappe.get_doc(
			'Purchase Invoice', 
			frappe.get_all('Purchase Invoice')[-1].name
		)
		
		pay_entry = frappe.get_doc(dict(
			doctype='Payment Entry',
			transaction_type=pur_invoice.doctype,
			reference_invoice=pur_invoice.name,
			payment_amount=5000
		))

		self.assertRaises(frappe.ValidationError, pay_entry.submit)




		