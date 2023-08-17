"""Toolbar UI."""
from trame.widgets import vuetify


def initialize(layout):
    """Initialize drawer layout."""
    with layout.toolbar:
        vuetify.VSpacer()
        file_input()


def file_input():
    """Set up File Input layout."""
    vuetify.VFileInput(
        show_size=True,
        small_chips=True,
        truncate_length=25,
        v_model=("file_exchange", None),
        dense=True,
        hide_details=True,
        style="max-width: 300px;"
    )
    vuetify.VProgressLinear(
        indeterminate=True, absolute=True, bottom=True, active=("trame__busy")
    )
