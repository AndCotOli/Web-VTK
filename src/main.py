import paraview.web.venv

import os
from pathlib import Path

from paraview import simple
from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vtk, vuetify, paraview

server = get_server()
state = server.state
ctrl = server.controller

paraview.initialize(server)

state.source_file = None
state.show_mesh = False
state.show_normals = False

model = {
    "actor": simple.Cone(),
    "display": None
}
model["display"] = simple.Show(model["actor"])
view = simple.Render()

def update_mapper():
    if state.source_file['type'] == "model/stl":
        path = str(Path().absolute().joinpath('temp.temp.stl'))
        with open(path, 'w') as file:
            for part in state.source_file['content']:
                file.write(part.decode('ascii'))
        simple.Delete(model["actor"])
        model["actor"] = simple.STLReader(registrationName="model.stl", FileNames=[path])
        model["display"] = simple.Show(model["actor"])
        ctrl.view_update()
        ctrl.view_reset_camera()
        os.remove(path)

def show_mesh():
    model["display"].SetRepresentationType("Surface" if state.show_mesh else "Wireframe")
    ctrl.view_update()

def show_normals():
    pass

ctrl.update_mapper = update_mapper
ctrl.show_mesh = show_mesh
ctrl.show_normals = show_normals

with SinglePageWithDrawerLayout(server) as layout:
    with layout.drawer as drawer:
        drawer.width = 325
        with vuetify.VContainer(fluid=True):
            vuetify.VFileInput(v_model="source_file")
            with vuetify.VBtn(click=ctrl.update_mapper):
                vuetify.VSubheader("Upload stl")
        vuetify.VDivider()
        with vuetify.VContainer(fluid=True):
            vuetify.VCheckbox(label="Show mesh", v_model=("show_mesh", False), change=ctrl.show_mesh)
            vuetify.VCheckbox(label="Show normals", v_model=("show_normals", False), change=ctrl.show_normals)

    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VDivider(vertical=True, classes="mx-2")
        with vuetify.VBtn(click=ctrl.view_reset_camera):
            vuetify.VSubheader("Reset Camera")

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            html_view = paraview.VtkLocalView(view)
            ctrl.view_update = html_view.update
            ctrl.view_reset_camera = html_view.reset_camera


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()