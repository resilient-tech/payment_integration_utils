import re
from datetime import datetime

import frappe
from constants.__init__ import SECONDS_IN_A_DAY
from frappe import _
from frappe.utils import (
    DateTimeLikeObject,
    add_to_date,
    get_timestamp,
    getdate,
)


################# PAYMENT UTILS #################
def is_already_paid(amended_from: str | None = None) -> bool | int:
    """
    Check if the Payment Entry is already paid via Bank Online Payment.

    :param amended_from: Original Payment Entry name.
    """
    if not amended_from:
        return False

    return frappe.db.get_value(
        "Payment Entry", amended_from, "make_bank_online_payment"
    )


################# APIs RELATED #################
def get_start_of_day_epoch(date: DateTimeLikeObject = None) -> int:
    """
    Return the Unix timestamp (seconds since Epoch) for the start of the given `date`.\n
    If `date` is None, the current date's start of day timestamp is returned.

    :param date: A date string in "YYYY-MM-DD" format or a (datetime,date) object.
    :return: Unix timestamp for the start of the given date.
    ---
    Example:
    ```
    get_start_of_day_epoch("2024-05-30") ==> 1717007400
    get_start_of_day_epoch(datetime(2024, 5, 30)) ==> 1717007400
    ```
    ---
    Note:
        - Unix timestamp refers to `2024-05-30 12:00:00 AM`
    """
    return int(get_timestamp(date))


def get_end_of_day_epoch(date: DateTimeLikeObject = None) -> int:
    """
    Return the Unix timestamp (seconds since Epoch) for the end of the given `date`.\n
    If `date` is None, the current date's end of day timestamp is returned.

    :param date: A date string in "YYYY-MM-DD" format or a (datetime,date) object.
    :return: Unix timestamp for the end of the given date.
    ---
    Example:
    ```
    get_end_of_day_epoch("2024-05-30") ==> 1717093799
    get_end_of_day_epoch(datetime(2024, 5, 30)) ==> 1717093799
    ```
    ---
    Note:
        - Unix timestamp refers to `2024-05-30 11:59:59 PM`
    """
    return int(get_timestamp(date)) + (SECONDS_IN_A_DAY - 1)


def get_str_datetime_from_epoch(epoch_time: int) -> str:
    """
    Get Local datetime from Epoch Time.\n
    Format: yyyy-mm-dd HH:MM:SS
    """
    return datetime.fromtimestamp(epoch_time).strftime("%Y-%m-%d %H:%M:%S")


def yesterday():
    """
    Get the date of yesterday from the current date.
    """
    return add_to_date(getdate(), days=-1)


def rupees_to_paisa(amount: float | int) -> int:
    """
    Convert the given amount in Rupees to Paisa.

    :param amount: The amount in Rupees to be converted to Paisa.

    Example:
    ```
    rupees_to_paisa(100) ==> 10000
    ```
    """
    return int(amount * 100)


def paisa_to_rupees(amount: int) -> int | float:
    """
    Convert the given amount in Paisa to Rupees.

    :param amount: The amount in Paisa to be converted to Rupees.

    Example:
    ```
    paisa_to_rupees(10000) ==> 100
    ```
    """
    return amount / 100


################# HTML RELATED #################
def get_unordered_list(items: list[str]) -> str:
    return "<ul>" + "".join([f"<li>{item}</li>" for item in items]) + "</ul>"


################# WRAPPERS #################
def enqueue_integration_request(**kwargs):
    frappe.enqueue(log_integration_request, **kwargs)


def log_integration_request(
    url=None,
    integration_request_service=None,
    request_id=None,
    request_headers=None,
    data=None,
    status=None,
    output=None,
    error=None,
    reference_doctype=None,
    reference_name=None,
    is_remote_request=False,
):
    def get_status():
        if status:
            return status

        return "Failed" if error else "Completed"

    return frappe.get_doc(
        {
            "doctype": "Integration Request",
            "integration_request_service": integration_request_service,
            "request_id": request_id,
            "url": url,
            "request_headers": pretty_json(request_headers),
            "data": pretty_json(data),
            "output": pretty_json(output),
            "error": pretty_json(error),
            "status": get_status(),
            "reference_doctype": reference_doctype,
            "reference_docname": reference_name,
            "is_remote_request": is_remote_request,
        }
    ).insert(ignore_permissions=True)


def pretty_json(obj):
    if not obj:
        return ""

    if isinstance(obj, str):
        return obj

    return frappe.as_json(obj, indent=4)


### String Manipulation ###
def to_hyphenated(text):
    """
    Replace any character that is not alphanumeric with a hyphen, including spaces.

    :param text: The text to be converted.

    ---
    Example:

    ```py
    convert_special_chars_to_hyphen("Hello World!") ==> "Hello-World-"
    ```
    """
    return re.sub(r"[^a-zA-Z0-9]", "-", text)
