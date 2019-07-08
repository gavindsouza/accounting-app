import frappe

@frappe.whitelist()
def say_hi():
    return "Hi"