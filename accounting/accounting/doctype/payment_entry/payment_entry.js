// Copyright (c) 2019, gvn and contributors
// For license information, please see license.tfieldt

frappe.ui.form.on('Payment Entry', {
	refresh: function (form) {
		form.trigger('filters');
		['paid_from', 'paid_to'].forEach(
			(field) => { form.toggle_reqd(field, true); }
		)
	},

	transaction_type: function (form) {
		form.trigger('filters');
	},

	filters: function (form) {
		if (form.doc.transaction_type === "Sales Invoice") {
			form.set_query("paid_from", () => { return { filters: { "is_group": 0, "parent_account": "Accounts Receivable" } } });
			form.set_query("paid_to", () => { return { filters: { "is_group": 0, "parent_account": "Cash in Hand" } } });
		} else if (form.doc.transaction_type === "Purchase Invoice") {
			form.set_query("paid_from", () => { return { filters: { "is_group": 0, "parent_account": "Cash in Hand" } } });
			form.set_query("paid_to", () => { return { filters: { "is_group": 0, "parent_account": "Accounts Payable" } } });
		}
	}
});
