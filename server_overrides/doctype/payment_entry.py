import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry
from frappe import _
from frappe.core.doctype.submission_queue.submission_queue import queue_submission
from frappe.utils import fmt_money, get_link_to_form
from frappe.utils.scheduler import is_scheduler_inactive

from constants.payments import BANK_METHODS
from constants.payments import TRANSFER_METHOD as PAYMENT_METHOD
from utils.__init__ import is_already_paid
from utils.auth import run_before_payment_authentication as has_payment_permissions
from utils.validation import validate_ifsc_code


#### DOC EVENTS ####
def onload(doc: PaymentEntry, method=None):
    doc.set_onload("is_already_paid", is_already_paid(doc.amended_from))

    doc.set_onload(
        "payment_integration_fields", frappe.get_hooks("payment_integration_fields")
    )

    doc.set_onload(
        "has_payment_permission", has_payment_permissions(doc.name, throw=False)
    )


def validate(doc: PaymentEntry, method=None):
    validate_if_already_paid(doc)

    # maybe occur when doc is duplicated
    if (
        doc.party_bank_account
        and not doc.make_bank_online_payment
        and doc.payment_transfer_method == PAYMENT_METHOD.LINK.value
    ):
        doc.payment_transfer_method = PAYMENT_METHOD.NEFT.value

    if (
        not doc.make_bank_online_payment
        or not doc.integration_docname
        or not doc.integration_doctype
    ):
        return

    validate_transfer_methods(doc, method)


### VALIDATION HELPERS ###
def validate_if_already_paid(doc: PaymentEntry):
    if not doc.amended_from:
        return

    payout_fields = [
        # Common
        "payment_type",
        "bank_account",
        # Party
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
        # Integration
        "integration_doctype",
        "integration_docname",
        # Payment
        "paid_amount",
        "make_bank_online_payment",
        "payment_transfer_method",
        "reference_no",
        *frappe.get_hooks("payment_integration_fields"),
    ]

    original_doc = frappe.db.get_value(
        "Payment Entry",
        doc.amended_from,
        payout_fields,
        as_dict=True,
    )

    if not original_doc or not original_doc.make_bank_online_payment:
        return

    for field in payout_fields:
        if doc.get(field) != original_doc.get(field):
            msg = _("Field <strong>{0}</strong> cannot be changed.<br><br>").format(
                doc.meta.get_label(field)
            )
            msg += _(
                "The source Payment Entry <strong>{0}</strong> is already processed via online payment integration.<br>"
            ).format(get_link_to_form("Payment Entry", doc.amended_from))

            frappe.throw(
                title=_("Payment Details Cannot Be Changed"),
                msg=msg,
            )

    # used in next actions and validations
    doc.flags._is_already_paid = True


def validate_transfer_methods(doc: PaymentEntry, method=None):
    validate_bank_payment_method(doc)
    validate_upi_payment_method(doc)
    validate_link_payment_method(doc)


def validate_bank_payment_method(doc: PaymentEntry):
    if doc.payment_transfer_method not in BANK_METHODS:
        return

    if not (
        doc.party_bank_account and doc.party_bank_account_no and doc.party_bank_ifsc
    ):
        frappe.throw(
            msg=_(
                "Party's Bank Account Details is mandatory to make payment. <br> Please set valid <strong>Party Bank Account</strong>."
            ),
            title=_("Mandatory Fields Missing"),
            exc=frappe.MandatoryError,
        )

    validate_ifsc_code(doc.party_bank_ifsc, throw=True)

    if (
        doc.payment_transfer_method == PAYMENT_METHOD.IMPS.value
        and doc.paid_amount > 5_00_000
    ):
        frappe.throw(
            msg=_(
                "<strong>IMPS</strong> transfer limit is {0}. Please use <strong>RTGS/NEFT</strong> for higher amount."
            ).format(fmt_money(5_00_000, currency="INR")),
            title=_("Payment Limit Exceeded"),
            exc=frappe.ValidationError,
        )

    if (
        doc.payment_transfer_method == PAYMENT_METHOD.RTGS.value
        and doc.paid_amount < 2_00_000
    ):
        frappe.throw(
            msg=_(
                "<strong>RTGS</strong> transfer minimum amount is {0}. Please use <strong>NEFT/IMPS</strong> for lower amount."
            ).format(fmt_money(2_00_000, currency="INR")),
            title=_("Insufficient Payment Amount"),
            exc=frappe.ValidationError,
        )


def validate_upi_payment_method(doc: PaymentEntry):
    if doc.payment_transfer_method != PAYMENT_METHOD.UPI.value:
        return

    if not (doc.party_upi_id and doc.party_bank_account):
        frappe.throw(
            msg=_(
                "Party's UPI ID is mandatory to make payment. Please set valid <strong>Party Bank Account</strong>."
            ),
            title=_("Mandatory Fields Missing"),
            exc=frappe.MandatoryError,
        )


def validate_link_payment_method(doc: PaymentEntry):
    if doc.payment_transfer_method != PAYMENT_METHOD.LINK.value:
        return

    if doc.party_type != "Employee" and not doc.contact_person:
        frappe.throw(
            msg=_("Contact Person is mandatory to make payment with link."),
            title=_("Mandatory Field Missing"),
            exc=frappe.MandatoryError,
        )

    # get contact details of party
    contact_details = get_party_contact_details(doc)
    party_mobile = contact_details["contact_mobile"]
    party_email = contact_details["contact_email"]

    if (
        not doc.contact_email
        and not doc.contact_mobile
        and (party_email or party_mobile)
    ):
        # why db_set? : if calls from API, then it will not update the value without db_set
        doc.db_set({"contact_email": party_email, "contact_mobile": party_mobile})

    if not party_email and not party_mobile:
        if doc.party_type == "Employee":
            msg = _(
                "Set Employee's Mobile or Preferred Email to make payment with link."
            )
        else:
            msg = _("Set valid Contact to make payment with link.")

        frappe.throw(
            msg=msg,
            title=_("Contact Details Missing"),
            exc=frappe.MandatoryError,
        )

    if doc.contact_mobile and doc.contact_mobile != party_mobile:
        frappe.throw(
            msg=_("Mobile Number does not match with Party's Mobile Number"),
            title=_("Invalid Mobile Number"),
        )

    if doc.contact_email and doc.contact_email != party_email:
        frappe.throw(
            msg=_("Email ID does not match with Party's Email ID"),
            title=_("Invalid Email ID"),
        )


def get_party_contact_details(doc: PaymentEntry) -> dict | None:
    """
    Get Party's contact details as Payment Entry's contact fields.

    - Mobile Number
    - Email ID
    """
    if doc.party_type == "Employee":
        return frappe.get_value(
            "Employee",
            doc.party,
            ["cell_number as contact_mobile", "prefered_email as contact_email"],
            as_dict=True,
        )

    return frappe.get_value(
        "Contact",
        doc.contact_person,
        ["mobile_no as contact_mobile", "email_id as contact_email"],
        as_dict=True,
    )


### APIs ###
@frappe.whitelist()
def bulk_pay_and_submit(
    auth_id: str,
    docnames: list[str] | str,
    mark_online_payment: bool | None = False,
    task_id: str | None = None,
):
    """
    Bulk pay and submit Payment Entries.

    :param auth_id: Authentication ID (after otp or password verification)
    :param docnames: List of Payment Entry to pay and submit
    :param mark_online_payment: Check `make_bank_online_payment` field
    :param task_id: Task ID (realtime or background)

    ---
    Reference: [Frappe Bulk Submit/Cancel](https://github.com/frappe/frappe/blob/3eda272bd61b1e73b74d30b1704d885a39c75d0c/frappe/desk/doctype/bulk_update/bulk_update.py#L51)
    """

    if isinstance(docnames, str):
        docnames = frappe.parse_json(docnames)

    has_payment_permissions(docnames, throw=True)

    if len(docnames) < 20:
        return _bulk_pay_and_submit(
            auth_id,
            docnames,
            mark_online_payment,
            task_id,
        )
    elif len(docnames) <= 500:
        frappe.msgprint(_("Bulk operation is enqueued in background."), alert=True)
        frappe.enqueue(
            _bulk_pay_and_submit,
            auth_id=auth_id,
            docnames=docnames,
            mark_online_payment=mark_online_payment,
            task_id=task_id,
            queue="short",
            timeout=1000,
        )
    else:
        frappe.throw(
            _("Bulk operations only support up to 500 documents."),
            title=_("Too Many Documents"),
        )


def _bulk_pay_and_submit(
    auth_id: str,
    docnames: list[str],
    mark_online_payment: bool | None = False,
    task_id: str | None = None,
):
    """
    Bulk pay and submit Payment Entries.

    :param auth_id: Authentication ID (after otp or password verification)
    :param docnames: List of Payment Entry to pay and submit
    :param mark_online_payment: Check `make_bank_online_payment` field
    :param task_id: Task ID (realtime or background)

    ---
    Reference: [Frappe Bulk Action](https://github.com/frappe/frappe/blob/3eda272bd61b1e73b74d30b1704d885a39c75d0c/frappe/desk/doctype/bulk_update/bulk_update.py#L73)
    """
    failed = []

    num_documents = len(docnames)

    for idx, docname in enumerate(docnames, 1):
        doc = frappe.get_doc("Payment Entry", docname)
        doc.set_onload("auth_id", auth_id)

        if mark_online_payment:
            doc.make_bank_online_payment = 1

        try:
            message = ""
            if doc.docstatus.is_draft():
                if doc.meta.queue_in_background and not is_scheduler_inactive():
                    queue_submission(doc, "submit")
                    message = _("Queuing {0} for Submission").format("Payment Entry")
                else:
                    doc.submit()
                    message = _("Submitting {0}").format("Payment Entry")
            else:
                failed.append(docname)

            frappe.db.commit()
            frappe.publish_progress(
                percent=idx / num_documents * 100,
                title=message,
                description=docname,
                task_id=task_id,
            )

        except Exception:
            failed.append(docname)
            frappe.db.rollback()

    return failed
