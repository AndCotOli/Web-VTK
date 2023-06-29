import os

from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vtk, vuetify

from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkIOGeometry import vtkSTLReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
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
# VTK pipeline
# -----------------------------------------------------------------------------

renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

cone_source = vtkConeSource()
mapper = vtkPolyDataMapper()
mapper.SetInputConnection(cone_source.GetOutputPort())
actor = vtkActor()
actor.SetMapper(mapper)

renderer.AddActor(actor)
renderer.ResetCamera()

# -----------------------------------------------------------------------------
# Trame
# -----------------------------------------------------------------------------

server = get_server()
state = server.state
ctrl = server.controller

state.source_file = None
state.show_mesh = False
state.show_normals = False

stlReader = vtkSTLReader()

def update_mapper():
    if state.source_file['type'] == "model/stl":
        with open("temp.stl", 'w') as file:
            for part in state.source_file['content']:
                file.write(part.decode('ascii'))
        stlReader.SetFileName("temp.stl")
        mapper.SetInputConnection(stlReader.GetOutputPort())
        ctrl.view_update()
        ctrl.view_reset_camera()
        os.remove("temp.stl")

def show_mesh():
    prop = actor.GetProperty()
    if not state.show_mesh: # Flip is backwards (False = Show mesh - True = Don't show mesh)
        prop.SetRepresentationToWireframe()
    else:
        prop.SetRepresentationToSurface()
    ctrl.view_update()

with SinglePageWithDrawerLayout(server) as layout:
    with layout.drawer as drawer:
        drawer.width = 325
        with vuetify.VContainer(fluid=True):
            vuetify.VFileInput(v_model="source_file")
            with vuetify.VBtn(click=update_mapper):
                vuetify.VSubheader("Upload stl")
        vuetify.VDivider()
        with vuetify.VContainer(fluid=True):
            vuetify.VCheckbox(label="Show mesh", v_model=("show_mesh", False), change=show_mesh)
            vuetify.VCheckbox(label="Show normals", v_model=("show_normals", False), change=lambda: print(f"Show mesh normals to: {state.show_normals}"))

    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VDivider(vertical=True, classes="mx-2")
        vuetify.VBtn()

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            view = vtk.VtkLocalView(renderWindow)
            ctrl.view_update = view.update
            ctrl.view_reset_camera = view.reset_camera


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()