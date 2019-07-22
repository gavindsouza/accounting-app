# -*- coding: utf-8 -*-
# Copyright (c) 2019, gvn and Contributors
# See license.txt

# imports - stndard imports
from __future__ import unicode_literals
import unittest

# imports - module imports
import frappe


class TestPartyType(unittest.TestCase):
	def setUp(self):
		if not frappe.db.exists('Party Type', 'Supplier'):
			frappe.get_doc({
				'doctype': 'Party Type',
				'party_type': 'Supplier',
				'account_type': 'Payable'
			}).insert()
		
		if not frappe.db.exists('Party Type', 'Customer'):
			frappe.get_doc({
				'doctype': 'Party Type',
				'party_type': 'Customer',
				'account_type': 'Receivable'
			}).insert()

	def test_delete_party_type(self):
		doc = frappe.get_doc('Party Type','Supplier')
		doc.delete()
		# self.assertRaises(frappe.LinkExistsError, doc.delete)
