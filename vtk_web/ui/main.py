"""Main UI."""
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.assets.local import LocalFileManager


from .toolbar import initialize as initialize_toolbar
from .drawer import initialize as initilize_drawer
from .viewer import initialize as initialize_viewer


def initialize(server):
    """Initialize ui."""
    state = server.state

    state.trame__title = "Commlab VTK"
    # state.trame__favicon = get_favicon()

    set_up_layout(server)


def get_favicon():
    """Get favicon."""
    asset_manager = LocalFileManager(__file__)
    return asset_manager.url("icon", "./assets/logo.png")


def set_up_layout(server):
    """Set up initial layout."""
    with SinglePageWithDrawerLayout(server) as layout:
        layout.title.set_text("Commlab VTK")
        initialize_viewer(layout, server)
        initialize_toolbar(layout, server)
        initilize_drawer(layout, server)

        layout.footer.hide()
