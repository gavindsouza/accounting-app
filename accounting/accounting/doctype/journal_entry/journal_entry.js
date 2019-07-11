// Copyright (c) 2019, gvn and contributors
// For license information, please see license.txt

frappe.ui.form.on('Journal Entry', {
	set_summary: function (form) {
		let total_debit = 0;
		let total_credit = 0;

		form.doc.journal_entry_table.forEach((row) => {
			total_credit += row.credit || 0;
			total_debit += row.debit || 0;
		});

		form.set_value("total_debit", total_debit);
		form.set_value("total_credit", total_credit);
		form.set_value("difference", (total_debit - total_credit));
	},

	refresh: function (form) {
		form.set_query("account", "journal_entry_table", () => { return { filters: { "is_group": 0 } } });
	}
});

frappe.ui.form.on('Journal Entry Table', {
	debit: function (form, cdt, cdn) {
		form.trigger('set_summary');
	},

	credit: function (form, cdt, cdn) {
		form.trigger('set_summary');
	},

	account: function (form, cdt, cdn) {
		let difference = form.fields_dict.difference.value;

		if (difference < 0) {
			locals[cdt][cdn].debit = Math.abs(difference);
		} else if (difference > 0) {
			locals[cdt][cdn].credit = Math.abs(difference);
		}

		form.trigger('set_summary');
		form.refresh_fields();
	}
});