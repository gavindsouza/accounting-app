// Copyright (c) 2019, gvn and contributors
// For license information, please see license.txt

{% include 'accounting/public/js/custom.js' %}

frappe.ui.form.on('Sales Invoice', {
	set_total_amount: function (form) {
		let calculated_amount = 0;
		form.doc.items.forEach((row) => {
			calculated_amount += row.item_amount;
		});
		form.set_value("total_amount", calculated_amount);
		form.refresh_fields();
	},
	
	refresh: function (form) {
		form.set_query("debit_to", () => { return { filters: { "is_group": 0, "parent_account": "Accounts Receivable" } } });
		form.set_query("assets_account", () => { return { filters: { "is_group": 0, "parent_account": "Stock Assets" } } });
		form.set_query("party", () => { return { filters: { "group": "Customer" } } });
		form.set_query("item", "items", () => { return { filters: { "labelled": "Sold" } } });
		make_payment_entry(form);
		add_button_to_general_ledger(form);
	}
});

// cdt, cdn = currentDocType, currentDocName
frappe.ui.form.on('Invoice Item', {
	item_quantity: function (form, cdt, cdn) {
		let curr_item = locals[cdt][cdn];
		
		if (parseInt(curr_item.fraction_allowed) === 0) {
			curr_item.item_quantity = Math.round(curr_item.item_quantity);
			form.refresh_fields();
		}
		
		curr_item.item_amount = curr_item.item_rate * curr_item.item_quantity || 0;
		form.refresh_field('items')
		form.trigger('set_total_amount');

	},

	item_rate: function (form, cdt, cdn) {
		let curr_item = locals[cdt][cdn];
		curr_item.item_amount = curr_item.item_rate * curr_item.item_quantity || 0;
		form.refresh_field('items')
		form.trigger('set_total_amount');
	},

	item_amount: function (form, cdt, cdn) {
		let curr_item = locals[cdt][cdn];
		locals[cdt][cdn].item_amount = curr_item.item_quantity * curr_item.item_rate || 0;
		form.trigger('set_total_amount');
	}
});