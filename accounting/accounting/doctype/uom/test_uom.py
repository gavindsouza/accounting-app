# -*- coding: utf-8 -*-
# Copyright (c) 2019, gvn and Contributors
# See license.txt

# imports - stndard imports
from __future__ import unicode_literals
import unittest

# imports - module imports
import frappe


def create_uom():
	if not frappe.db.exists('UOM', 'Kg'):
		frappe.get_doc({
			'doctype': 'UOM',
			'uom_name': 'Kg',
			'uom_fraction': 0
		}).insert()


class TestUOM(unittest.TestCase):
	def setUp(self):
		create_uom()
