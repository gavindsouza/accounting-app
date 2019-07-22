# -*- coding: utf-8 -*-
# Copyright (c) 2019, gvn and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

# def create_payment_entry():
# 	doc = frappe.get_doc({
# 		'doctype': 'Payment Entry',
# 		'transaction_type': 'Purchase Invoice',
# 		'reference_invoice': '',
# 		'paid_from': '',
# 		'paid_to': '',
# 		'payment_amount': ''
# 	})
# 	if not frappe.db.exists(doc):
# 		doc.insert()


# class TestPaymentEntry(unittest.TestCase):
# 	def setUp(self):
# 		create_payment_entry()

# 	def test_make_payment_entry(self):
# 		pur_invoice = frappe.get_doc(
# 			'Purchase Invoice', 
# 			frappe.get_all('Purchase Invoice')[-1].name
# 		)



