app_name = "payment_integration_utils"
app_title = "Payment Integration Utils"
app_publisher = "Resilient Tech"
app_description = "Base for integrate online payment integrations"
app_email = "info@resilient.tech"
app_license = "GNU General Public License (v3)"
# required_apps = ["frappe/erpnext"]

after_install = "payment_integration_utils.install.after_install"
before_uninstall = "payment_integration_utils.uninstall.before_uninstall"

app_include_js = "payment_integration_utils.bundle.js"

export_python_type_annotations = True

doctype_js = {
    "Payment Entry": "payment_integration_utils/client_overrides/form/payment_entry.js",
    "Bank Account": "payment_integration_utils/client_overrides/form/bank_account.js",
    "User": "payment_integration_utils/client_overrides/form/user.js",
}

doctype_list_js = {
    "Payment Entry": "payment_integration_utils/client_overrides/list/payment_entry_list.js",
}


doc_events = {
    "Payment Entry": {
        "onload": "payment_integration_utils.payment_integration_utils.server_overrides.doctype.payment_entry.onload",
        "validate": "payment_integration_utils.payment_integration_utils.server_overrides.doctype.payment_entry.validate",
    },
    "Bank Account": {
        "validate": "payment_integration_utils.payment_integration_utils.server_overrides.doctype.bank_account.validate",
    },
}

before_payment_authentication = "payment_integration_utils.payment_integration_utils.utils.permission.has_payment_permissions"
