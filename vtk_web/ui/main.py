"""Main UI."""
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.assets.local import LocalFileManager


from .toolbar import initialize as initialize_toolbar
from .drawer import initialize as initilize_drawer


def initialize(server):
    """Initialize ui."""
    state, ctrl = server.state, server.controller

    state.trame__title = "Commlab VTK"
    state.trame__favicon = get_favicon()

    ctrl.on_data_change.add(ctrl.view_update)

    set_up_layout(server)


def get_favicon():
    """Get favicon."""
    asset_manager = LocalFileManager(__file__)
    return asset_manager.url("icon", "./assets/logo.png")


def set_up_layout(server):
    """Set up initial layout."""
    with SinglePageWithDrawerLayout(server) as layout:
        layout.title.set_text("Commlab VTK")
        initialize_toolbar(layout)
        initilize_drawer(layout, server.controller)

        layout.footer.hide()
