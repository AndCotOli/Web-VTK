import tempfile

from trame.app import get_server
from trame.app.file_upload import ClientFile
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vuetify, html

import pyvista as pv
from pyvista.trame.ui import get_or_create_viewer

import numpy as np

from scripts.vtk2www_inlet_outlets import default_inlet_outlets

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

pv.OFF_SCREEN = True

server = get_server()
state, ctrl = server.state, server.controller

state.trame__title = "File Viewer"
ctrl.on_server_ready.add(ctrl.view_update)

plotter = pv.Plotter()

# -----------------------------------------------------------------------------
# State
# -----------------------------------------------------------------------------

@server.state.change("file_exchange")
def file_handle(file_exchange, **kwargs):
    file = ClientFile(file_exchange)

    if file.content:
        print(file.info)
        bytes = file.content
        with tempfile.NamedTemporaryFile(suffix=file.name) as path:
            with open(path.name, 'wb') as f:
                f.write(bytes)
            ds = pv.read(path.name)
            ds.compute_normals(inplace=True)
        plotter.add_mesh(ds, name=file.name)
        plotter.reset_camera()
    else:
        plotter.clear_actors()
        plotter.reset_camera()

@server.state.change("mesh_visibility")
def mesh_visibility_change(mesh_visibility, **kwargs):
    for _, actor in plotter.actors.items():
        actor.prop.show_edges = mesh_visibility
    ctrl.view_update()

@server.state.change("normal_visibility")
def normal_visibility_change(normal_visibility, **kwargs):
    # for _, actor in plotter.actors.items():
    #     actor.mapper.dataset.plot_normals()
    ctrl.view_update()

@server.state.change("inlet_visibility")
def inlet_visibility_change(inlet_visibility, **kwargs):
    for _, actor in plotter.actors.items():
        mesh = actor.mapper.dataset
        inlet, outlets, outlets_wall_distance = default_inlet_outlets(mesh)

# -----------------------------------------------------------------------------
# Web App setup
# -----------------------------------------------------------------------------

state.trame__title = "File Viewer"

viewer = get_or_create_viewer(plotter)

with SinglePageWithDrawerLayout(server) as layout:
    layout.title.set_text("File Viewer")
    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VFileInput(
            show_size=True,
            small_chips=True,
            truncate_length=25,
            v_model=("file_exchange", None),
            dense=True,
            hide_details=True,
            style="max-width: 300px;",
        )
        vuetify.VProgressLinear(
            indeterminate=True, absolute=True, bottom=True, active=("trame__busy",)
        )

    with layout.drawer:
        with vuetify.VContainer(fluid=True):
            with vuetify.VContainer(fluid=True):
                with vuetify.VBtn(click=ctrl.view_reset_camera):
                    vuetify.VSubheader("Reset Camera")
            vuetify.VDivider()
            with vuetify.VContainer(fluid=True):
                vuetify.VCheckbox(
                    label="Show mesh", 
                    v_model=("mesh_visibility", False)
                )
                vuetify.VCheckbox(
                    label="Show normals",
                    v_model=("normal_visibility", False)
                )
            vuetify.VDivider()
            with vuetify.VContainer(fluid=True):
                vuetify.VCheckbox(
                    label="Show inlets",
                    v_model=("inlet_visibility", False)
                )
        
    with layout.content:
        with vuetify.VContainer(
            fluid=True, classes="pa-0 fill-height", style="position: relative;"
        ):
            view = viewer.ui(add_menu=False, mode="trame", default_server_rendering=False)
            ctrl.view_update = view.update
            ctrl.view_reset_camera = view.reset_camera

    layout.footer.hide()

server.start()