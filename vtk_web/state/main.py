"""Main state controller."""
from .visibility import initialize as initialize_visibility
from .file_input import initialize as initialize_file_input


def initialize(server):
    """Initialize state."""
    ctrl = server.controller

    initialize_visibility(server)
    initialize_file_input(server)

    ctrl.on_server_ready(ctrl.view_update)
