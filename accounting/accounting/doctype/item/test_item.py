# -*- coding: utf-8 -*-
# Copyright (c) 2019, gvn and Contributors
# See license.txt

# imports - standard imports
from __future__ import unicode_literals
import unittest

# imports - module imports
import frappe
from accounting.accounting.doctype.uom.test_uom import create_uom

# test dependencies
test_dependencies = ['UOM']


class TestItem(unittest.TestCase):
	def setUp(self):
		create_uom()

	def test_make_item_with_missing_mandatory_field(self):
		doc = frappe.get_doc({
			'doctype': 'Item',
			'item_id': 'test_ID001',
			'labelled': 'Sold',
			'item_name': 'test_NAME001',
			'selling_rate': 1000
		})
		self.assertRaises(frappe.exceptions.MandatoryError, doc.insert)

	def test_make_item(self):
		if not frappe.db.exists('Item', 'test_item_001'):
			frappe.get_doc({
				'doctype': 'Item',
				'item_id': 'test_item_001',
				'item_uom': 'Kg',
				'labelled': 'Sold',
				'selling_rate': 1000,
				'item_name': 'test_item_001'
			}).insert()
