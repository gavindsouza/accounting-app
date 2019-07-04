// Copyright (c) 2019, gvn and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Invoice', {
	set_total_amount: function (form) {
		let calculated_amount = 0;
		form.doc.items.forEach((row) => {
			calculated_amount += row.item_amount;
		});
		form.set_value("total_amount", calculated_amount);
		form.refresh_fields();
	},

	refresh: function (form) {
		form.set_query("credit_to", () => { return { filters: { "is_group": 0, "parent_account": "Accounts Payable" } } });
		form.set_query("assets_account", () => { return { filters: { "is_group": 0, "parent_account": "Stock Assets" } } });
		form.set_query("supplier", () => { return { filters: { "group": "Supplier" } } });
		form.set_query("item", "items", () => { return { filters: { "labelled": "Purchased" } } });
	}
});

frappe.ui.form.on('Invoice Item', {
	item_quantity: function (form, cdt, cdn) {
		let curr_item = locals[cdt][cdn];
		curr_item.item_amount = curr_item.item_rate * curr_item.item_quantity;
		form.refresh_field('items')
		form.trigger('set_total_amount');
	},

	item_rate: function (form, cdt, cdn) {
		let curr_item = locals[cdt][cdn];
		curr_item.item_amount = curr_item.item_rate * curr_item.item_quantity;
		form.refresh_field('items')
		form.trigger('set_total_amount');
	},

	item_amount: function (form, cdt, cdn) {
		let curr_item = locals[cdt][cdn];
		locals[cdt][cdn].item_amount = flt(curr_item.item_quantity) * flt(curr_item.item_rate);
		form.trigger('set_total_amount');
	}
});