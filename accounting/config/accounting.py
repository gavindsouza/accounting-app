from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "label": _("To begin with"),
            "icon": "octicon octicon-briefcase",
            "items": [
                {
                    "name": "Item",
                    "type": "doctype",
                    "label": _("Item"),
                    "description": _("stuff in the ERP"),
                    "items": []
                },
                {
                    "name": "Party",
                    "type": "doctype",
                    "label": _("Party"),
                    "description": _("customer supplier"),
                    "items": []
                }
            ],
        },
        {
            "label": _("Reports"),
            "items": [
                {
                    "name": "General Ledger",
                    "type": "doctype",
                    "label": _("General Ledger"),
                    "description": _(""),
                    "items": []
                }
            ]
        },       
        {
            "label": _("Transactions"),
            "icon": "octicon octicon-briefcase",
            "items": [
                {
                    "name": "Sales Invoice",
                    "type": "doctype",
                    "label": _("Sales Invoice"),
                    "description": _(""),
                    "items": []
                },
                {
                    "name": "Purchase Invoice",
                    "type": "doctype",
                    "label": _("Purchase Invoice"),
                    "description": _(""),
                    "items": []
                },
                {
                    "name": "Journal Entry",
                    "type": "doctype",
                    "label": _("Journal Entry"),
                    "description": _(""),
                    "items": []
                }
            ]
        },
        {
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
            ]
        }
    ]
