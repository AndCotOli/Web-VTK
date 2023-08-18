"""Main state controller."""
from .visibility import initialize as initialize_visibility


def initialize(server):
    """Initialize state."""
    initialize_visibility(server)
