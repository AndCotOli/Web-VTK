"""
Version for trame 1.x - https://github.com/Kitware/trame/blob/release-v1/examples/VTK/Applications/MultiFilter/app.py
Delta v1..v2          - https://github.com/Kitware/trame/commit/7b3cda7c45b8a60132892f762e16ed28cb709481
"""

from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vtk, vuetify, trame
from trame.assets.remote import HttpFile

from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkFiltersCore import vtkContourFilter
from vtkmodules.vtkIOXML import vtkXMLUnstructuredGridReader
from vtkmodules.vtkIOGeometry import vtkSTLReader

from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

# Required for interactor initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa

# Required for rendering initialization, not necessary for
# local rendering, but doesn't hurt to include it
import vtkmodules.vtkRenderingOpenGL2  # noqa

# -----------------------------------------------------------------------------
# Data file information
# -----------------------------------------------------------------------------

dataset_file = "./data/model.stl"
 

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------


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
# VTK pipeline
# -----------------------------------------------------------------------------

renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

# Read Data
reader = vtkSTLReader() # vtkXMLUnstructuredGridReader()
reader.SetFileName(dataset_file)
reader.Update()

# Mesh
mesh_mapper = vtkDataSetMapper()
mesh_mapper.SetInputConnection(reader.GetOutputPort())
mesh_actor = vtkActor()
mesh_actor.SetMapper(mesh_mapper)
renderer.AddActor(mesh_actor)

# Mesh: Setup default representation to surface
mesh_actor.GetProperty().SetRepresentationToSurface()
mesh_actor.GetProperty().SetPointSize(1)
mesh_actor.GetProperty().EdgeVisibilityOff()

# Mesh: Apply rainbow color map
mesh_lut = mesh_mapper.GetLookupTable()
mesh_lut.SetHueRange(0.666, 0.0)
mesh_lut.SetSaturationRange(1.0, 1.0)
mesh_lut.SetValueRange(1.0, 1.0)
mesh_lut.Build()

# Mesh: Color by default array
#mesh_mapper.SelectColorArray(default_array.get("text"))
#mesh_mapper.GetLookupTable().SetRange(default_min, default_max)
#if default_array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
#    mesh_mapper.SetScalarModeToUsePointFieldData()
#else:

mesh_mapper.SetScalarModeToUseCellFieldData()
mesh_mapper.SetScalarVisibility(True)
mesh_mapper.SetUseLookupTableScalarRange(True)

vcs_actor = vtkActor()


# Cube Axes
cube_axes = vtkCubeAxesActor()
renderer.AddActor(cube_axes)

# Cube Axes: Boundaries, camera, and styling
cube_axes.SetBounds(mesh_actor.GetBounds())
cube_axes.SetCamera(renderer.GetActiveCamera())
cube_axes.SetXLabelFormat("%6.1f")
cube_axes.SetYLabelFormat("%6.1f")
cube_axes.SetZLabelFormat("%6.1f")
cube_axes.SetFlyModeToOuterEdges()

renderer.ResetCamera()

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller

state.setdefault("active_ui", None)

# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------


@state.change("cube_axes_visibility")
def f(cube_axes_visibility, **kwargs):
    cube_axes.SetVisibility(cube_axes_visibility)
    ctrl.view_update()


# Selection Change
def actives_change(ids):
    _id = ids[0]
    if _id == "1":  # Mesh
        state.active_ui = "mesh"
    elif _id == "2":  # VCS
        state.active_ui = "vcs"
    else:
        state.active_ui = "nothing"


# Visibility Change
def visibility_change(event):
    _id = event["id"]
    _visibility = event["visible"]

    if _id == "1":  # Mesh
        mesh_actor.SetVisibility(_visibility)
    elif _id == "2":  # Contour
        vcs_actor.SetVisibility(_visibility)
    ctrl.view_update()


# Representation Callbacks
def update_representation(actor, mode):
    property = actor.GetProperty()
    if mode == Representation.Points:
        property.SetRepresentationToPoints()
        property.SetPointSize(2)
        property.EdgeVisibilityOff()
    elif mode == Representation.Wireframe:
        property.SetRepresentationToWireframe()
        property.SetPointSize(1)
        property.EdgeVisibilityOff()
    elif mode == Representation.Surface:
        property.SetRepresentationToSurface()
        property.SetPointSize(1)
        property.EdgeVisibilityOff()
    elif mode == Representation.SurfaceWithEdges:
        property.SetRepresentationToSurface()
        property.SetPointSize(1)
        property.EdgeVisibilityOn()


@state.change("mesh_representation")
def update_mesh_representation(mesh_representation, **kwargs):
    update_representation(mesh_actor, mesh_representation)
    ctrl.view_update()


# Color By Callbacks
def color_by_array(actor, array):
    _min, _max = array.get("range")
    mapper = actor.GetMapper()
    mapper.SelectColorArray(array.get("text"))
    mapper.GetLookupTable().SetRange(_min, _max)
    if array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
        mesh_mapper.SetScalarModeToUsePointFieldData()
    else:
        mesh_mapper.SetScalarModeToUseCellFieldData()
    mapper.SetScalarVisibility(True)
    mapper.SetUseLookupTableScalarRange(True)


# Color Map Callbacks
def use_preset(actor, preset):
    lut = actor.GetMapper().GetLookupTable()
    if preset == LookupTable.Rainbow:
        lut.SetHueRange(0.666, 0.0)
        lut.SetSaturationRange(1.0, 1.0)
        lut.SetValueRange(1.0, 1.0)
    elif preset == LookupTable.Inverted_Rainbow:
        lut.SetHueRange(0.0, 0.666)
        lut.SetSaturationRange(1.0, 1.0)
        lut.SetValueRange(1.0, 1.0)
    elif preset == LookupTable.Greyscale:
        lut.SetHueRange(0.0, 0.0)
        lut.SetSaturationRange(0.0, 0.0)
        lut.SetValueRange(0.0, 1.0)
    elif preset == LookupTable.Inverted_Greyscale:
        lut.SetHueRange(0.0, 0.666)
        lut.SetSaturationRange(0.0, 0.0)
        lut.SetValueRange(1.0, 0.0)
    lut.Build()



@state.change("chosenFile")
def update_mesh(chosenFile, **kwargs):
    print("loaded mesh:", chosenFile)
    ctrl.view_update()

def chosenFile():
    state.chosenFile = not state.chosenFile

@state.change("mesh_color_preset")
def update_mesh_color_preset(mesh_color_preset, **kwargs):
    use_preset(mesh_actor, mesh_color_preset)
    ctrl.view_update() 

# Opacity Callbacks
@state.change("mesh_opacity")
def update_mesh_opacity(mesh_opacity, **kwargs):
    mesh_actor.GetProperty().SetOpacity(mesh_opacity)
    ctrl.view_update()

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

def run_vcs():
    state.run_vcs = not state.run_vcs

# -----------------------------------------------------------------------------
# GUI elements
# -----------------------------------------------------------------------------


def standard_buttons():
    vuetify.VCheckbox(
        v_model=("cube_axes_visibility", True),
        on_icon="mdi-cube-outline",
        off_icon="mdi-cube-off-outline",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )
    vuetify.VCheckbox(
        v_model="$vuetify.theme.dark",
        on_icon="mdi-lightbulb-off-outline",
        off_icon="mdi-lightbulb-outline",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )
    vuetify.VCheckbox(
        v_model=("viewMode", "local"),
        on_icon="mdi-lan-disconnect",
        off_icon="mdi-lan-connect",
        true_value="local",
        false_value="remote",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )
    with vuetify.VBtn(icon=True, click="$refs.view.resetCamera()"):
        vuetify.VIcon("mdi-crop-free")


def pipeline_widget():
    trame.GitTree(
        sources=(
            "pipeline",
            [
                {"id": "1", "parent": "0", "visible": 1, "name": "Mesh"},
                {"id": "2", "parent": "1", "visible": 1, "name": "Vessel Coordinate System"},
            ],
        ),
        actives_change=(actives_change, "[$event]"),
        visibility_change=(visibility_change, "[$event]"),
    )


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


def mesh_card():
    with ui_card(title="Mesh", ui_name="mesh"):
       
        vuetify.VFileInput(
            label = "STL mesh file",
             v_model= ("chosenFile", "inputFile"),

        )
        vuetify.VSelect(
            # Representation
            v_model=("mesh_representation", Representation.Surface),
            items=(
                "representations",
                [
                    {"text": "Points", "value": 0},
                    {"text": "Wireframe", "value": 1},
                    {"text": "Surface", "value": 2},
                    {"text": "SurfaceWithEdges", "value": 3},
                ],
            ),
            label="Representation",
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1",
        )
    
        with vuetify.VCol(cols="6"):
            vuetify.VSelect(
                # Color Map
                label="Colormap",
                v_model=("mesh_color_preset", LookupTable.Rainbow),
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
        vuetify.VSlider(
            # Opacity
            v_model=("mesh_opacity", 1.0),
            min=0,
            max=1,
            step=0.1,
            label="Opacity",
            classes="mt-1",
            hide_details=True,
            dense=True,
        )

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
            click = run_vcs,
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


# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

with SinglePageWithDrawerLayout(server) as layout:
    layout.title.set_text("Viewer")

    with layout.toolbar:
        # toolbar components
        vuetify.VSpacer()
        vuetify.VDivider(vertical=True, classes="mx-2")
        standard_buttons()

    with layout.drawer as drawer:
        # drawer components
        drawer.width = 325
        pipeline_widget()
        vuetify.VDivider(classes="mb-2")
        mesh_card()
        vcs_card()

    with layout.content:
        # content components
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            # view = vtk.VtkRemoteView(renderWindow, interactive_ratio=1)
            # view = vtk.VtkLocalView(renderWindow)
            view = vtk.VtkRemoteLocalView(
                renderWindow, namespace="view", mode="local", interactive_ratio=1
            )
            ctrl.view_update = view.update
            ctrl.view_reset_camera = view.reset_camera
            ctrl.on_server_ready.add(view.update)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
