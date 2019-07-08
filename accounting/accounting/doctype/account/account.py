# -*- coding: utf-8 -*-
# Copyright (c) 2019, gvn and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
from frappe.utils.nestedset import NestedSet
import frappe


class Account(NestedSet):
    nsm_parent_field = 'parent_account'