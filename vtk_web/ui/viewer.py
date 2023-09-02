"""VTK viewer ui."""
from pyvista.trame.ui import get_viewer
from trame.widgets import vuetify

from vtk_web.plotter import plotter


def initialize(layout, server):
    """Initialize VTK view."""
    ctrl = server.controller
    viewer = get_viewer(plotter)
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

            ctrl.view_get_rendering_state = lambda *args, **kwargs: (
                viewer.SERVER_RENDERING)
            ctrl.view_update = view.update
            ctrl.view_reset_camera = view.reset_camera
            ctrl.view_push_camera = view.push_camera
