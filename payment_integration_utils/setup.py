import click
import frappe
from frappe.custom.doctype.custom_field.custom_field import (
    create_custom_fields as make_custom_fields,
)

from payment_integration_utils.payment_integration_utils.constants.custom_fields import (
    CUSTOM_FIELDS,
)
from payment_integration_utils.payment_integration_utils.constants.property_setters import (
    PROPERTY_SETTERS,
)
from payment_integration_utils.payment_integration_utils.constants.roles import ROLES
from payment_integration_utils.payment_integration_utils.constants.workflows import (
    STATES_COLORS as WORKFLOW_STATES,
)
from payment_integration_utils.payment_integration_utils.constants.workflows import (
    WORKFLOW_ACTION,
    WORKFLOWS,
)
from payment_integration_utils.payment_integration_utils.setup import (
    delete_custom_fields,
    delete_property_setters,
    delete_roles_and_permissions,
    make_roles_and_permissions,
    make_workflow_actions,
    make_workflow_states,
    make_workflows,
)


################### After Install ###################
def setup_customizations():
    click.secho("Creating Roles and Permissions...", fg="blue")
    create_roles_and_permissions()

    click.secho("Creating Custom Fields...", fg="blue")
    create_custom_fields()

    click.secho("Creating Property Setters...", fg="blue")
    create_property_setters()

    click.secho("Creating Workflows...", fg="blue")
    create_workflows()


# Note: separate functions are required to use in patches
def create_roles_and_permissions():
    make_roles_and_permissions(ROLES)


def create_custom_fields():
    make_custom_fields(CUSTOM_FIELDS)


def create_property_setters():
    for property_setter in PROPERTY_SETTERS:
        frappe.make_property_setter(property_setter)


def create_workflows():
    # create states
    make_workflow_states(WORKFLOW_STATES)

    # create actions
    make_workflow_actions(WORKFLOW_ACTION.values())

    # create workflows
    make_workflows(WORKFLOWS)


################### Before Uninstall ###################
def delete_customizations():
    click.secho("Deleting Custom Fields...", fg="blue")
    delete_custom_fields(CUSTOM_FIELDS)

    click.secho("Deleting Property Setters...", fg="blue")
    delete_property_setters(PROPERTY_SETTERS)

    click.secho("Deleting Roles and Permissions...", fg="blue")
    delete_roles_and_permissions(ROLES)
