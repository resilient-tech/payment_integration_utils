from payment_integration_utils.payment_integration_utils.setup import (
    delete_custom_fields,
)

FIELDS_TO_DELETE = {"Payment Entry": ["is_auto_generated"]}


def execute():
    delete_custom_fields(FIELDS_TO_DELETE)
