from __future__ import unicode_literals
from frappe import _


def get_data():
    to_begind_with = {
        "label": _("To begin with"),
        "icon": "octicon octicon-briefcase",
        "items": [
            {
                "name": "Item",
                "type": "doctype",
                "label": _("Item"),
                "description": _("stuff in the ERP")
            },
            {
                "name": "Party",
                "type": "doctype",
                "label": _("Party"),
                "description": _("customer supplier")
            }
        ]
    }

    transactions = {
        "label": _("Transactions"),
        "icon": "octicon octicon-briefcase",
        "items": [
            {
                "name": "Sales Invoice",
                "type": "doctype",
                "label": _("Sales Invoice")
            },
            {
                "name": "Purchase Invoice",
                "type": "doctype",
                "label": _("Purchase Invoice")
            },
            {
                "name": "Journal Entry",
                "type": "doctype",
                "label": _("Journal Entry")
            }
        ]
    }

    meat_and_potatoes = {
        "label": _("Meat & Potatoes"),
        "type": "module",
        "items": [
            {
                "name": "Account",
                "type": "doctype",
                "label": _("Chart of Accounts"),
                "description": _("accounting structure: chart of acc"),
                "route": "#Tree/Account"
            },
            {
                "name": "General Ledger",
                "type": "report",
                "label": _("General Ledger"),
                "doctype": "GL Entry",
                "is_query_report": True
            },
            {
                "name": "Trial Balance",
                "type": "report",
                "label": _("Trial Balance"),
                "doctype": "GL Entry",
                "is_query_report": True
            }
        ]
    }

    return [
        to_begind_with,
        transactions,
        meat_and_potatoes
    ]
