"""Main file."""
from trame.app import get_server
from ui.main import initialize as initialize_ui


def main(server=None):
    """Start the server."""
    if server is None:
        server = get_server()

    server.client_type = "vue2"

    initialize_ui(server)

    return server.start()


if __name__ == "__main__":
    server = get_server()
    main(server)
