"""Toolbar UI."""
from trame.widgets import vuetify


def initialize(layout, server):
    """Initialize toolbar layout."""
    state = server.state
    with layout.toolbar:
        vuetify.VSpacer()
        file_input(state)


def file_input(state):
    """Set up File Input layout."""
    vuetify.VFileInput(
        show_size=True,
        truncate_length=25,
        v_model=("file_exchange", None),
        dense=True,
        hide_details="auto",
        label="STL Model",
        loading=False
    )
