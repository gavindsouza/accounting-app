# -*- coding: utf-8 -*-
# Copyright (c) 2019, gvn and Contributors
# See license.txt

# imports - stndard imports
from __future__ import unicode_literals
import unittest

# imports - module imports
import frappe

# test dependencies
test_dependencies = ['Party Type']


class TestParty(unittest.TestCase):
	def setUp(self):
		frappe.get_doc({
			'doctype': 'Party',
			'party_id': 'test_party_001',
			'party_name': 'test_party_name_001',
			'group': 'Supplier'
		})

	def test_abc(self):
		pass

	def tearDown(self):
		frappe.delete_doc('Party', 'test_party_001')
