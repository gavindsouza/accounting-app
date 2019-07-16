frappe.provide("frappe.treeview_settings")

frappe.treeview_settings['Account'] = {
	get_tree_nodes: "accounting.api.get_children",
	onrender: function (node) {
		if (frappe.boot.user.can_read.indexOf("GL Entry") !== -1) {
			if (node.data && node.data.account_balance !== undefined && node.data.account_balance != 0) {
				let symbol = node.data.account_balance > 0 ? 'Dr' : 'Cr';
				$('<span class="balance-area pull-right text-muted small">'
					+ format_currency(node.data.account_balance, 'INR') + ' ' + symbol
					+ '</span>').insertBefore(node.$ul);
			}
		}
	}
}