// Copyright (c) 2016, gvn and contributors
// For license information, please see license.txt

frappe.query_reports["Trial Balance"] = {
	"filters": [
		{
			"fieldname": "account",
			"label": __("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"get_query": function () {
				return {
					"doctype": "Account",
					"filters": {
						'is_group': false
					}
				}
			}
		},
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": "2019-2020",
			// function () {
			// 	let today = frappe.datetime.get_today();
			// 	frappe.db.get_list('Fiscal Year').then(fiscal_year => {
			// 		fiscal_year.forEach(row => {
			// 			// return row.name
			// 			console.log(row)
			// 			if (row.year_start_date > today > row.year_end_date) {
			// 				return row.name
			// 			}
			// 		})
			// 	});
			// },
			"on_change": function (query_report) {
				let fiscal_year = query_report.get_values().fiscal_year;
				if (!fiscal_year) {
					return;
				}
				frappe.model.with_doc("Fiscal Year", fiscal_year, function (r) {
					let fy = frappe.get_doc("Fiscal Year", fiscal_year);
					frappe.query_report.set_filter_value({
						from_date: fy.year_start_date,
						to_date: fy.year_end_date
					});
				});
			}
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (!data.parent_account || data.parent_account === 'Company Root') {
			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");
			if (data.warn_if_negative && data[column.fieldname] < 0) {
				$value.addClass("text-danger");
			}

			value = $value.wrap("<p></p>").parent().html();
		}

		return value;
	}
}
