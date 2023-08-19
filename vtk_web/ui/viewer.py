"""VTK viewer ui."""
from pyvista.trame.ui import get_or_create_viewer
from trame.widgets import vuetify


from plotter import plotter


def initialize(layout, server):
    """Initialize VTK view."""
    ctrl = server.controller
    viewer = get_or_create_viewer(plotter)
    with layout.content:
        with vuetify.VContainer(
                fluid=True,
                classes="pa-0 fill-height",
                style="position: relative;"
        ):
            view = viewer.ui(
                add_menu=False,
                mode="trame",
                default_server_rendering=False
            )

            ctrl.view_update = view.update
            ctrl.view_reset_camera = view.reset_camera