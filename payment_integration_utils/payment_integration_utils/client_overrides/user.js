// Copyright (c) 2025, Resilient Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on("User", {
	refresh: function (frm) {
		if (
			!is_2fa_otp_app_enabled() ||
			!frappe.user.has_role(payment_integration_utils.PAYOUT_AUTHORIZER) ||
			frappe.session.user != frm.doc.name
		) {
			return;
		}

		frm.add_custom_button(
			__("Reset Payment OTP Secret"),
			function () {
				frappe.call({
					method: `${payment_integration_utils.AUTH_MODULE}.reset_otp_secret`,
					args: {
						user: frm.doc.name,
					},
				});
			},
			__("Password")
		);
	},
});

function is_2fa_otp_app_enabled() {
	return (
		cint(frappe.boot.sysdefaults.enable_two_factor_auth) &&
		frappe.boot.sysdefaults.two_factor_method === payment_integration_utils.AUTH_METHODS.OTP_APP
	);
}
