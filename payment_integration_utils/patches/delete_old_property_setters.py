from payment_integration_utils.payment_integration_utils.setup import (
    delete_property_setters,
)

PROPERTY_SETTERS_TO_DELETE = []


def execute():
    delete_property_setters(PROPERTY_SETTERS_TO_DELETE)
