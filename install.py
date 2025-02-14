import click
import frappe
from payment_integration_utils_mode_co.constants import BUG_REPORT_URL
from payment_integration_utils_mode_co.hooks import app_title as APP_NAME
from payment_integration_utils_mode_co.setup import setup_customizations

POST_INSTALL_PATCHES = []


def after_install():
    try:
        setup_customizations()
        run_post_install_patches()

    except Exception as e:
        click.secho(
            (
                f"Installation of {APP_NAME} failed due to an error. "
                "Please try re-installing the app or "
                f"report the issue on {BUG_REPORT_URL} if not resolved."
            ),
            fg="bright_red",
        )
        raise e

    click.secho(f"Thank you for installing {APP_NAME}!!\n", fg="green")


def run_post_install_patches():
    if not POST_INSTALL_PATCHES:
        return

    click.secho("Running post-install patches...", fg="yellow")

    frappe.flags.in_patch = True

    try:
        for patch in POST_INSTALL_PATCHES:
            patch_module = (
                f"payment_integration_utils.patches.post_install.{patch}.execute"
            )
            frappe.get_attr(patch_module)()

    finally:
        frappe.flags.in_patch = False
