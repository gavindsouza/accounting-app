import frappe
from frappe.utils import cint


@frappe.whitelist()
def get_children(doctype, parent='', filters=None, is_root=None):
    leaves = frappe.get_list('Account',
                             filters={'parent_account': parent},
                             fields=['name as value', 'account_balance', 'parent_account', 'is_group as expandable'])
    return leaves


@frappe.whitelist()
def make_payment_entry(reference_invoice, transaction_type, paid_from, paid_to):
    doctype_name = 'Payment Entry'
    instance_doc = {
        'doctype': doctype_name,
        'reference_invoice': reference_invoice,
        'transaction_type': transaction_type
    }

    if not frappe.db.exists(instance_doc):
        doc = frappe.get_doc(instance_doc)
        doc.paid_from = paid_from
        doc.paid_to = paid_to
        doc.insert()
        doc_name = doc.name

    else:
        doc_name = frappe.db.get_value(
            doctype_name,
            {'reference_invoice': reference_invoice},
            ['name']
        )

    return doc_name
