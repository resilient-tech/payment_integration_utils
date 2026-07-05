// Copyright (c) 2025, Resilient Tech and contributors
// For license information, please see license.txt

// Pay-driver registry: a backend claims a PE via integration_doctype, then swaps
// what "Pay and Submit" DOES without touching the button/label/toggle/dialogs.
// No driver for a doctype -> the default RazorpayX behaviour (savesubmit on the
// form, OTP + bulk_pay_and_submit on the list).
//
// driver = {
//   form(frm),              // pay-and-submit one PE; default: frm.savesubmit()
//   bulk(list_view, docs),  // pay-and-submit these docs; default: OTP + bulk_pay_and_submit
//   add_fields: [...],      // extra list columns the driver's eligibility needs
// }

frappe.provide("payment_integration_utils");

payment_integration_utils.pay_drivers = payment_integration_utils.pay_drivers || {};

payment_integration_utils.register_pay_driver = function (integration_doctype, driver) {
    payment_integration_utils.pay_drivers[integration_doctype] = driver;
};

// The driver for a PE's integration_doctype, or null for the default flow.
payment_integration_utils.get_pay_driver = function (integration_doctype) {
    return payment_integration_utils.pay_drivers[integration_doctype] || null;
};
