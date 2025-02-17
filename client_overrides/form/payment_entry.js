// Copyright (c) 2025, Resilient Tech and contributors
// For license information, please see license.txt

const PAYMENT_FIELDS = [
	// Common
	"payment_type",
	"bank_account",
	// Party
	"party",
	"party_type",
	"party_name",
	"party_bank_account",
	"party_bank_account_no",
	"party_bank_ifsc",
	"party_upi_id",
	"contact_person",
	"contact_mobile",
	"contact_email",
	// Integration
	"integration_doctype",
	"integration_docname",
	// Payment
	"paid_amount",
	"make_bank_online_payment",
	"payment_transfer_method",
	"reference_no",
];

frappe.ui.form.on("Payment Entry", {
	refresh: async function (frm) {
		// Do not allow to edit fields if Payment is processed by RazorpayX in amendment
		await disable_payout_fields_in_amendment(frm);

		// update descriptions
		frm.get_field("payment_type").set_empty_description();
		frm.get_field("reference_no").set_empty_description();
	},

	validate: function (frm) {
		if (!frm.doc.integration_doctype || !frm.doc.integration_docname) {
			if (frm.doc.make_bank_online_payment) {
				frm.set_value("make_bank_online_payment", 0);
			}

			return;
		}

		if (!frm.doc.make_bank_online_payment) return;

		if (frm.doc.payment_transfer_method === payment_integration_utils.PAYMENT_TRANSFER_METHOD.LINK) {
			if (!frm.doc.contact_mobile && !frm.doc.contact_email) {
				let msg = "";

				if (frm.doc.party_type === "Employee") {
					msg = __("Set Employee's Mobile or Preferred Email to make payout with link.");
				} else {
					msg = __("Any one of Party's Mobile or Email is mandatory to make payout with link.");
				}

				frappe.throw({ message: msg, title: __("Contact Details Missing") });
			}
		}

		payment_integration_utils.validate_payment_transfer_method(
			frm.doc.payment_transfer_method,
			frm.doc.paid_amount
		);
	},

	bank_account: function (frm) {
		if (!frm.doc.bank_account) {
			frm.set_value("make_bank_online_payment", 0);
		}
	},

	party: async function (frm) {
		if (frm.doc.contact_mobile) frm.set_value("contact_mobile", "");

		if (frm.doc.party_type !== "Employee" || !frm.doc.party) return;

		const details = await payment_integration_utils.get_employee_contact_details(frm.doc.party);

		if (details) frm.set_value(details);
	},

	party_bank_account: function (frm) {
		if (!frm.doc.party_bank_account) {
			frm.set_value("payment_transfer_method", payment_integration_utils.PAYMENT_TRANSFER_METHOD.LINK);
		} else {
			frm.set_value("payment_transfer_method", payment_integration_utils.PAYMENT_TRANSFER_METHOD.NEFT);
		}
	},

	contact_person: function (frm) {
		if (!frm.doc.contact_person && frm.doc.contact_mobile) {
			frm.set_value("contact_mobile", "");
		}
	},
});

// ############ UTILITY ############ //
/**
 * If current Payment Entry is amended from another Payment Entry,
 * and original Payment Entry is processed (not mean by status) by RazorpayX, then disable
 * payout fields in the current Payment Entry.
 */
async function disable_payout_fields_in_amendment(frm) {
	if (!frm.doc.amended_from || frm.doc.docstatus == 2) return;

	let is_paid = payment_integration_utils.is_already_paid(frm);

	if (is_paid === undefined) {
		const response = await frappe.db.get_value(
			"Payment Entry",
			frm.doc.amended_from,
			"make_bank_online_payment"
		);

		is_paid = response.message?.make_bank_online_payment || 0;
	}

	PAYMENT_FIELDS.push(...(payment_integration_utils.get_onload(frm, "payment_integration_fields") || []));
	frm.toggle_enable(PAYMENT_FIELDS, is_paid ? 0 : 1);
}
