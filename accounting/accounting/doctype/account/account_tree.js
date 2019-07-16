frappe.provide("frappe.treeview_settings")

frappe.treeview_settings['Account'] = {
	get_tree_nodes: "accounting.api.get_children",
	onload: function (form) {
	},

	onrender: function (node) {
		if (frappe.boot.user.can_read.indexOf("GL Entry") !== -1) {
			var dr_or_cr = node.data.account_balance < 0 ? "Cr" : "Dr";

			if (node.data && node.data.account_balance !== undefined && node.data.account_balance != 0) {
				$('<span class="balance-area pull-right text-muted small">'
					+ format_currency(Math.abs(node.data.account_balance), 'INR')
					+ " " + dr_or_cr
					+ '</span>').insertBefore(node.$ul);
			}
		}
	}
}