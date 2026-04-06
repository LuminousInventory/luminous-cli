"""Contacts resource."""

import typer

from luminous_cli.cli.resources._factory import ResourceSpec, make_resource_group
from luminous_cli.client import get_client

spec = ResourceSpec(
    name="contacts",
    singular="contact",
    api_path="/contacts",
    columns=[
        ("ID", "id", "dim"),
        ("Name", "full_name", ""),
        ("Email", "email", "cyan"),
        ("Phone", "phone_1", ""),
        ("Company", "company.name", ""),
        ("Primary", "is_primary", ""),
        ("Updated", "updated_at", "dim"),
    ],
    capabilities={"list", "get", "create", "update", "delete"},
)

group = make_resource_group(spec)


@group.command("set-password")
def set_password(
    contact_id: int = typer.Argument(..., help="Contact ID"),
    password: str = typer.Option(..., "--password", prompt=True, hide_input=True, help="B2B portal password"),
) -> None:
    """Set or rotate B2B portal password for a contact."""
    client = get_client()
    client.request("POST", f"/contacts/{contact_id}/password", json_body={"password": password})
    typer.echo(f"Password set for contact {contact_id}")
