// Copyright (c) 2016, gvn and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["General Ledger"] = {
	"filters": [
		{
            "label": __("Fiscal Year"),
            "fieldname": "fiscal_year",
			"fieldtype": "Link",
			"options": "Fiscal Year",
			on_change: function(){
				let fiscal_year = frappe.query_report.get_filter_value('fiscal_year');
				frappe.db.get_value('Fiscal Year', fiscal_year, ['year_start_date', 'year_end_date']).then(
					response => {
						let values = response.message;
						frappe.query_report.set_filter_value('from_date', values.year_start_date);
						frappe.query_report.set_filter_value('to_date', values.year_end_date);
					});
			}
        },
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "transaction_type",
			"label": __("Transaction Type"),
			"fieldtype": "Select",
			"options": [
				"",
				__("Purchase Invoice"),
				__("Sales Invoice"),
				__("Journal Entry")
			]
		},
		{
			"fieldname": "account",
			"label": __("Account"),
			"fieldtype": "Link",
			"options": "Account"
		}
	]
};
