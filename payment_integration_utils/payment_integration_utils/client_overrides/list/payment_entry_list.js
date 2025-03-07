// Copyright (c) 2025, Resilient Tech and contributors
// For license information, please see license.txt

frappe.listview_settings["Payment Entry"] = {
	add_fields: ["make_bank_online_payment", "integration_docname", "integration_doctype"],

	onload: function (list_view) {
		// Add `Pay and Submit` button to the Payment Entry list view
		if (!payment_integration_utils.can_user_authorize_payment()) return;

		list_view.page.add_actions_menu_item(__("Pay and Submit"), () => {
			const selected_docs = list_view.get_checked_items();
			const marked_docs = [];
			const unmarked_docs = [];
			const ineligible_docs = [];

			selected_docs.forEach((doc) => {
				if (can_make_payment(doc)) {
					if (doc.make_bank_online_payment) marked_docs.push(doc.name);
					else unmarked_docs.push(doc.name);
				} else {
					ineligible_docs.push({ name: doc.name, reason: get_ineligibility_reason(doc) });
				}
			});

			if (!marked_docs.length && !unmarked_docs.length) {
				let message = __("Please select valid payment entries to pay and submit.");

				if (ineligible_docs.length) {
					message += "<br>";
					message += get_ineligible_docs_html(
						ineligible_docs,
						__("View Ineligible Docs ({0})", [ineligible_docs.length])
					);
				}

				frappe.msgprint(message, __("Invalid Selection"));
				return;
			}

			show_confirm_dialog(list_view, marked_docs, unmarked_docs, ineligible_docs);
		});
	},
};

// #### Utils #### //
function can_make_payment(doc) {
	return (
		doc.integration_doctype &&
		doc.integration_docname &&
		doc.docstatus === 0 &&
		doc.payment_type === "Pay"
	);
}

function get_ineligibility_reason(doc) {
	if (!doc.integration_doctype || !doc.integration_docname) {
		return __("Integration missing");
	} else if (doc.docstatus !== 0) {
		return __("Not Submittable");
	} else if (doc.payment_type !== "Pay") {
		return __("Not Payable");
	}
}

// #### Dialog #### //
function show_confirm_dialog(list_view, marked_docs, unmarked_docs, ineligible_docs) {
	const dialog = new frappe.ui.Dialog({
		title: __("Confirm Payment Entries"),
		primary_action_label: __("Confirm"),
		fields: [
			{
				fieldname: "eligible_doc_count_html",
				fieldtype: "HTML",
				options: `<p>✅ ${__("Marked for online payment: {0}", [marked_docs.length])} </p>`,
				depends_on: `eval: ${marked_docs.length} && (${unmarked_docs.length} || ${ineligible_docs.length})`,
			},
			{
				fieldname: "eligible_doc_html",
				fieldtype: "HTML",
				options: __("Pay and Submit {0} Documents?", [marked_docs.length]),
				depends_on: `eval: ${marked_docs.length} && ${!unmarked_docs.length}`,
			},
			{
				fieldtype: "Section Break",
				fieldname: "sec_unmarked_docs",
				depends_on: `eval: ${unmarked_docs.length}`,
			},
			{
				fieldname: "unmarked_doc_html",
				fieldtype: "HTML",
				options: get_unmarked_docs_html(unmarked_docs),
				depends_on: `eval: ${unmarked_docs.length}`,
			},
			{
				fieldname: "mark_online_payment",
				label: __("Mark make online payment"),
				fieldtype: "Check",
				default: unmarked_docs.length ? 1 : 0,
				depends_on: `eval: ${unmarked_docs.length}`,
				description: `<p class='text-info font-weight-bold'>
								${__("Note: If unchecked, Unmarked docs will be skipped!")}
							</p>`,
			},
			{
				fieldtype: "Section Break",
				fieldname: "sec_ineligible_docs",
				depends_on: `eval: ${ineligible_docs.length}`,
			},
			{
				fieldname: "ineligible_doc_html",
				fieldtype: "HTML",
				options: get_ineligible_docs_html(
					ineligible_docs,
					__("To be skipped ({0})", [ineligible_docs.length])
				),
				depends_on: `eval: ${ineligible_docs.length}`,
			},
		],

		primary_action: (values) => {
			dialog.hide();

			if (!marked_docs.length && (!unmarked_docs.length || !values.mark_online_payment)) {
				list_view.clear_checked_items();
				frappe.show_alert(__("No payment entries to pay and submit."));
				return;
			}

			if (!values.mark_online_payment) unmarked_docs = [];

			const docnames = [...marked_docs, ...unmarked_docs];

			list_view.disable_list_update = true;

			payment_integration_utils.authenticate_payment_entries(docnames, (auth_id) => {
				// Reference: https://github.com/frappe/frappe/blob/3eda272bd61b1e73b74d30b1704d885a39c75d0c/frappe/public/js/frappe/list/list_view.js#L1983
				pay_and_submit(auth_id, docnames, values.mark_online_payment);

				list_view.disable_list_update = false;
				list_view.clear_checked_items();
				list_view.refresh();
			});
		},
	});

	dialog.show();
}
function get_formlink(doc) {
	return `<a target="_blank" href="${frappe.utils.get_form_link("Payment Entry", doc)}">${doc}</a>`;
}

function get_unmarked_docs_html(docs) {
	if (!docs.length) return "";

	return `<details open>
				<summary>${__("Not marked for online payment ({0})", [docs.length])}</summary>
				<ol>${docs.map((doc) => `<li>${get_formlink(doc)}</li>`).join("")}</ol>
			</details>`;
}

function get_ineligible_docs_html(docs, summary, open = false) {
	if (!docs.length) return "";

	return `<details ${open ? "open" : ""}>
				<summary>${summary}</summary>
				<ol>${docs.map((doc) => `<li>${get_formlink(doc.name)}: ${doc.reason}</li>`).join("")}</ol>
			</details>`;
}

// #### API Call #### //
function pay_and_submit(auth_id, docnames, mark_online_payment = false, callback = null) {
	// Reference: https://github.com/frappe/frappe/blob/3eda272bd61b1e73b74d30b1704d885a39c75d0c/frappe/public/js/frappe/list/bulk_operations.js#L275
	if (!docnames.length) return;

	const task_id = Math.random().toString(36).slice(-5);
	frappe.realtime.task_subscribe(task_id);

	frappe.show_alert({
		message: __("Pay and Submitting {0} Payment Entry...", [docnames.length]),
		indicator: "blue",
	});

	return frappe
		.xcall(
			"payment_integration_utils.payment_integration_utils.server_overrides.doctype.payment_entry.bulk_pay_and_submit",
			{
				auth_id: auth_id,
				docnames: docnames,
				mark_online_payment: mark_online_payment,
				task_id: task_id,
			}
		)
		.then((failed_docnames) => {
			if (failed_docnames?.length) {
				const comma_separated_records = frappe.utils.comma_and(failed_docnames);
				frappe.throw(__("Cannot pay and submit {0}.", [comma_separated_records]));
			}

			frappe.utils.play_sound("submit");
			callback && callback();
		})
		.finally(() => {
			frappe.realtime.task_unsubscribe(task_id);
		});
}
