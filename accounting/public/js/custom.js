function make_payment_entry(form) {
    if (form.doc.docstatus == 1) {
        form.add_custom_button(
            __('Payment Entry'),
            () => {
                frappe.call({
                    'method': 'accounting.api.make_payment_entry',
                    'args': {
                        'reference_invoice': form.docname,
                        'transaction_type': form.doctype
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
