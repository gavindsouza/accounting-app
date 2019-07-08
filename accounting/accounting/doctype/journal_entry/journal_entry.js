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
	},

	on_submit: function (form) {
		frappe.msgprint("This got submitted");
	}
});

frappe.ui.form.on('Journal Entry Table', {
	debit: function (form, cdt, cdn) {
		form.trigger('set_summary');
	},

	credit: function (form, cdt, cdn) {
		form.trigger('set_summary');
	},

	account: function (frm, dt, dn) {
		let curr_row = locals[dt][dn];
		let last_row = frm.fields_dict.journal_entry_table.grid.last_docname;
		let grd = cur_frm.fields_dict.journal_entry_table.grid.grid_rows;

		let grd_len = grd.length;

		// if (grd_len > 1){
		// 	grd[grd_len].doc.credit = grd[grd_len - 1].doc.debit; 

		// 	frm.refresh_fields();
		// }

		console.log(grd_len);
	}
});