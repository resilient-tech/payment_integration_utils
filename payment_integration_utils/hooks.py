app_name = "payment_integration_utils"
app_title = "Payment Integration Utils"
app_publisher = "Resilient Tech"
app_description = "Base for integrate online payment integrations"
app_email = "info@resilient.tech"
app_license = "GNU General Public License (v3)"
required_apps = ["frappe/erpnext"]

after_install = "payment_integration_utils.install.after_install"
before_uninstall = "payment_integration_utils.uninstall.before_uninstall"

app_include_js = "payment_integration_utils.bundle.js"

export_python_type_annotations = True

doctype_js = {
    "Payment Entry": "payment_integration_utils/client_overrides/payment_entry.js",
    "Bank Account": "payment_integration_utils/client_overrides/bank_account.js",
    "User": "payment_integration_utils/client_overrides/user.js",
}

before_payment_authentication = "payment_integration_utils.payment_integration_utils.utils.permission.has_payment_permissions"
