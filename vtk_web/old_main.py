import tempfile

import numpy as np
import pyvista as pv
from pyvista.trame.ui import get_or_create_viewer
from trame.app import get_server
from trame.app.file_upload import ClientFile
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vuetify

from scripts.vtk2www_inlet_outlets import default_inlet_outlets


class Representation:
    Points = 0
    Wireframe = 1
    Surface = 2
    SurfaceWithEdges = 3


class LookupTable:
    Rainbow = 0
    Inverted_Rainbow = 1
    Greyscale = 2
    Inverted_Greyscale = 3

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

pv.OFF_SCREEN = True

server = get_server()
state, ctrl = server.state, server.controller

state.trame__title = "File Viewer"
ctrl.on_server_ready.add(ctrl.view_update)

state.setdefault("active_ui", None)

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


        intlets, outlets, _outlets_wall_dist = default_inlet_outlets(ds)
        outlets_border = ds.extract_feature_edges(boundary_edges=True, manifold_edges=False, feature_edges=False)
        connected_cells = outlets_border.connectivity()
        num_outlets = len(np.unique(connected_cells["RegionId"]))

        if num_outlets == 2:
            plotter.add_mesh(ds, name=file.name)
            plotter.reset_camera()
        else:
            print("Not a tube")
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
    ctrl.view_update()
    #for _, actor in plotter.actors.items():
    #    mesh = actor.mapper.dataset
    #    inlet, outlets, outlets_wall_distance = default_inlet_outlets(mesh)


@state.change("vcs_k_value")
def update_vcs_k(vcs_k_value, **kwargs):
    print("update vcs_k:", vcs_k_value)

@state.change("vcs_r_value")
def update_vcs_r(vcs_r_value, **kwargs):
    print("update vcs_r:", vcs_r_value)

@state.change("vcs_l_value")
def update_vcs_l(vcs_l_value, **kwargs):
    print("update vcs_t:", vcs_l_value)

@state.change("run_vcs")
def run(run_vcs, **kwargs):
    print("run vcs:", run_vcs)
    print("l,r,k:",state.vcs_l_value, state.vcs_r_value,state.vcs_k_value )

# -----------------------------------------------------------------------------
# Web App setup
# -----------------------------------------------------------------------------

def actives_change(ids):
    _id = ids[0]
    if _id == "1":  # Mesh
        state.active_ui = "mesh"
    elif _id == "2":  # VCS
        state.active_ui = "vcs"
    else:
        state.active_ui = "nothing"

def ui_card(title, ui_name):
    with vuetify.VCard(v_show=f"active_ui == '{ui_name}'"):
        vuetify.VCardTitle(
            title,
            classes="grey lighten-1 py-1 grey--text text--darken-3",
            style="user-select: none; cursor: pointer",
            hide_details=True,
            dense=True,
        )
        content = vuetify.VCardText(classes="py-2")
    return content

def vcs_card():
    with ui_card(title="VCS", ui_name="vcs"):

        vuetify.VSlider(
            # Contour Value
            v_model=("vcs_l_value", 0.5),
            min=("vcs_l_min", 2),
            max=("vcs_l_max", 50),
            step=("vcs_l_step", 1),
            label="VCS_L",
            classes="my-1",
            hide_details=True,
            dense=True,
            thumb_label = True,
        )
        vuetify.VSlider(
            # Contour Value
            v_model=("vcs_r_value", 0.5),
            min=("vcs_r_min", 2),
            max=("vcs_r_max", 50),
            step=("vcs_r_step", 1),
            label="VCS_R",
            classes="my-1",
            hide_details=True,
            dense=True,
            thumb_label = True,
        )
        vuetify.VSlider(
            # Contour Value
            v_model=("vcs_k_value", 0.5),
            min=("vcs_k_min", 2),
            max=("vcs_k_max", 50),
            step=("vcs_k_step", 1),
            label="VCS_K",
            classes="my-1",
            hide_details=True,
            dense=True,
            thumb_label = True,
        )

        vuetify.VTimeline()

        vuetify.VBtn(
            label = " Compute VCS ",
            click = lambda: None,
            block = True,
            classes="my-1",
            rounded = True,
            )

        vuetify.VTimeline()
        vuetify.VSelect(
            # Representation
            v_model=("vcs_representation", Representation.Surface),
            items=(
                "vcs_representations",
                [
                    {"text": "Ro", "value": 0},
                    {"text": "Tau", "value": 1},
                    {"text": "Sigma", "value": 2},
                    #{"text": "SurfaceWithEdges", "value": 3},
                ],
            ),
            label="VCS_Axis",
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
        )
        with vuetify.VCol(cols="6"):
            vuetify.VSelect(
                # Color Map
                label="Colormap",
                v_model=("contour_color_preset", LookupTable.Rainbow),
                items=(
                    "colormaps",
                    [
                        {"text": "Rainbow", "value": 0},
                        {"text": "Inv Rainbow", "value": 1},
                        {"text": "Greyscale", "value": 2},
                        {"text": "Inv Greyscale", "value": 3},
                    ],
                ),
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-1",
            )

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
        vcs_card()

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

if __name__ == "__main__":
    server.start()
