"""Main file."""
from trame.app import get_server
from vtk_web.ui import initialize as initialize_ui
from vtk_web.state import initialize as initialize_state


def main(server=None):
    """Start the server."""
    if server is None:
        server = get_server()

    initialize_ui(server)
    initialize_state(server)

    return server.start()


if __name__ == "__main__":
    server = get_server()
    main(server)
