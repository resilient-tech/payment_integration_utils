import click
import frappe
from constants.custom_fields import CUSTOM_FIELDS
from constants.property_setters import PROPERTY_SETTERS
from constants.roles import ROLES
from constants.workflows import STATES_COLORS as WORKFLOW_STATES
from constants.workflows import WORKFLOW_ACTION, WORKFLOWS
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from setup.__init__ import (
    delete_custom_fields,
    delete_property_setters,
    delete_roles_and_permissions,
    make_roles_and_permissions,
    make_workflow_actions,
    make_workflow_states,
    make_workflows,
)

NAME = "Payment Integration Utils"


################### After Install ###################
def setup_customizations():
    click.secho(f"Setting up {NAME} customizations...", fg="blue")

    make_roles_and_permissions(ROLES)

    create_custom_fields(CUSTOM_FIELDS)

    for property_setter in PROPERTY_SETTERS:
        frappe.make_property_setter(property_setter)

    # create states
    make_workflow_states(WORKFLOW_STATES)

    # create actions
    make_workflow_actions(WORKFLOW_ACTION.values())

    # create workflows
    make_workflows(WORKFLOWS)


################### Before Uninstall ###################
def delete_customizations():
    click.secho(f"Deleting {NAME} customizations...", fg="blue")

    delete_custom_fields(CUSTOM_FIELDS)

    delete_property_setters(PROPERTY_SETTERS)

    delete_roles_and_permissions(ROLES)
