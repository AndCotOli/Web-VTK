"""Main state controller."""
from .visibility import initialize as initialize_visibility
from .file_input import initialize as initialize_file_input


def initialize(server):
    """Initialize state."""
    initialize_visibility(server)
    initialize_file_input(server)
