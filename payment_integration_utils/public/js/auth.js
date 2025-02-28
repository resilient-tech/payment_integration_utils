const AUTH_METHODS = {
	OTP_APP: "OTP App",
	// TODO: @Implement SMS and Email
	// SMS: "SMS",
	// EMAIL: "Email",
};

const AUTH_MODULE = "payment_integration_utils.payment_integration_utils.utils.auth";

Object.assign(payment_integration_utils, {
	// ################ CONSTANTS ################ //
	AUTH_METHODS,

	AUTH_MODULE,

	// ################ UTILITIES ################ //
	/**
	 * Authenticate payment entries.
	 *
	 * Note: Only single OTP is generated for all the payment entries.
	 *
	 * @param {string | string[]} payment_entries - Payment Entry name or list of names
	 * @param {Function} callback - Callback function to be executed after successful authentication
	 */
	async authenticate_payment_entries(payment_entries, callback) {
		const get_otp_description = (generation_details) => {
			if (generation_details.setup) return __(generation_details.prompt);

			return `<bold class='text-danger font-weight-bold'>
						${frappe.utils.icon("solid-error")} &nbsp;
						${__("There is some error! Please contact your Administrator.")}
					</bold>`;
		};

		if (typeof payment_entries === "string") {
			payment_entries = [payment_entries];
		}

		const generation_details = await this.generate_otp(payment_entries);
		if (!generation_details) return;

		const dialog = new frappe.ui.Dialog({
			title: __("Enter OTP"),
			fields: [
				{
					fieldname: "info",
					fieldtype: "HTML",
					options: `<div class="alert alert-warning" role="alert">
            					${__("Do not close this dialog until you authenticate.")}
        					</div> <br>`,
				},
				{
					fieldname: "otp",
					label: __("OTP"),
					fieldtype: "Data",
					description: get_otp_description(generation_details),
					reqd: 1,
				},
			],
			minimizable: true,
			primary_action_label: __("Enter"),
			primary_action: async (values) => {
				const { verified, message } = await this.verify_otp(
					values.otp.trim(),
					generation_details.auth_id
				);

				if (verified) {
					dialog.hide();

					callback && callback(generation_details.auth_id);
					return;
				}

				// Invalid OTP
				const error = `<p class="text-danger font-weight-bold">
									${frappe.utils.icon("solid-error")} &nbsp;
									${__(message || "Invalid! Please try again.")}
								</p>`;

				const otp_field = dialog.get_field("otp");
				otp_field.set_new_description(error);

				// reset the description to the original
				setTimeout(() => {
					otp_field.set_new_description(otp_field.df.description);
				}, 3000);
			},
		});

		dialog.show();
	},

	/**
	 * Generate OTP for the given payment entries.
	 *
	 * Note: Only single OTP is generated for all the payment entries.
	 *
	 * @param {string[]} payment_entries List of Payment Entry names
	 *
	 * ---
	 * One Example Response:
	 * ```js
	 * {
	 * 	method: "OTP App",
	 *  auth_id: "12345678",
	 * 	setup: true,
	 * 	prompt: "Enter verification code from your OTP app",
	 * }
	 * ```
	 */
	async generate_otp(payment_entries) {
		const response = await frappe.call({
			method: `${AUTH_MODULE}.generate_otp`,
			args: {
				payment_entries,
			},
			freeze: true,
			freeze_message: __("Please wait..."),
		});

		return response?.message;
	},

	/**
	 * Verify the otp for the given auth_id.
	 *
	 * @param {string} otp OTP
	 * @param {string} auth_id Authentication ID
	 *
	 * ---
	 * Example Response:
	 * ```js
	 * {
	 * 	verified: true,
	 * 	message: "OTP verified successfully.",
	 * }
	 * ```
	 */
	async verify_otp(otp, auth_id) {
		const response = await frappe.call({
			method: `${AUTH_MODULE}.verify_otp`,
			args: { otp, auth_id },
			freeze: true,
			freeze_message: __("Verifying OTP..."),
		});

		return response?.message;
	},
});
