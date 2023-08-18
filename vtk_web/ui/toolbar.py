"""Toolbar UI."""
from trame.widgets import vuetify


def initialize(layout):
    """Initialize toolbar layout."""
    with layout.toolbar:
        vuetify.VSpacer()
        file_input()


def file_input():
    """Set up File Input layout."""
    vuetify.VFileInput(
        show_size=True,
        truncate_length=25,
        v_model=("file_exchange", None),
        dense=True,
        hide_details="auto",
        label="STL Model",
    )
    vuetify.VProgressLinear(
        indeterminate=True, absolute=True, bottom=True, active=("trame__busy")
    )
