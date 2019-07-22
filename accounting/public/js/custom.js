function make_payment_entry(form) {
    if (form.doc.docstatus == 1) {
        let paid_from, paid_to;
        if (form.doctype === "Sales Invoice") {
            paid_from = form.doc.debit_to;
            paid_to = 'Cash';
        } else if (form.doctype === "Purchase Invoice") {
            paid_from = 'Cash';
            paid_to = form.doc.credit_to;
        }
        form.add_custom_button(
            __('Payment Entry'),
            () => {
                frappe.call({
                    'method': 'accounting.api.make_payment_entry',
                    'args': {
                        'reference_invoice': form.docname,
                        'transaction_type': form.doctype,
                        'paid_from': paid_from,
                        'paid_to': paid_to
                    },
                    'callback': (response) => {
                        frappe.set_route(
                            'Form',
                            'Payment Entry',
                            response.message
                        );
                    }
                });
            },
            __('Create')
        );
    }
}

function add_button_to_general_ledger(form) {
    if (form.doc.docstatus > 0) {
        form.add_custom_button(
            __('Show General Ledger'),
            () => {
                frappe.set_route(
                    'query-report',
                    'General Ledger',
                    {
                        'voucher_type': form.doc.doctype,
                        'reference_document': form.doc.name
                    })
            },
            __('Reports')
        )
    }
}
