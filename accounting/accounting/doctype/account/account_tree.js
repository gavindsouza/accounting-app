frappe.provide("frappe.treeview_settings")

frappe.treeview_settings['Account'] = {
    onrender: function(node) {
		if(frappe.boot.user.can_read.indexOf("GL Entry") !== -1){
			// let dr_or_cr = node.data.balance < 0 ? "Cr" : "Dr";
            console.log(node.data.account_balance);
            // if (node.data && node.data.balance!==undefined) {
			// 	$('<span class="balance-area pull-right text-muted small">'
			// 		+ (node.data.balance_in_account_currency ?
			// 			(format_currency(Math.abs(node.data.balance_in_account_currency),
			// 				node.data.account_currency) + " / ") : "")
			// 		+ format_currency(Math.abs(node.data.balance), node.data.company_currency)
			// 		+ " " + dr_or_cr
			// 		+ '</span>').insertBefore(node.$ul);
			// }
		}
    }
};