"""File input state."""
from tempfile import NamedTemporaryFile

import pyvista as pv
import numpy as np
from plotter import plotter
from trame.app.file_upload import ClientFile

from scripts.vtk2www_inlet_outlets import default_inlet_outlets


def initialize(server):
    """Initialize file input state."""
    state, ctrl = server.state, server.controller

    @state.change("file_exchange")
    def file_exchange(file_exchange, **kwargs):
        plotter.clear_actors()

        file = ClientFile(file_exchange)

        if not is_valid_file(file):
            print("Invalid file")
            return

        bytes = file.content
        with NamedTemporaryFile(suffix=file.name) as path:
            with open(path.name, "wb") as f:
                f.write(bytes)
            ds = pv.read(path.name)

            if not is_valid_mesh(ds):
                print("Invalid mesh")
                return

            plotter.add_mesh(ds, name="mesh", reset_camera=True)

        ctrl.view_update()


def is_valid_file(file):
    """Check if the file is valid (i.e non-empty and .stl)."""
    return not file.is_empty and file.mime_type == "model/stl"


def is_valid_mesh(mesh):
    """Check if mesh is valid (i.e it is a tube)."""
    inlets, outlets, outlets_wall_dist = default_inlet_outlets(mesh)
    outlets_border = mesh.extract_feature_edges(
        boundary_edges=True,
        manifold_edges=False,
        feature_edges=False
    )
    connected_cells = outlets_border.connectivity()
    num_outlets = len(np.unique(connected_cells["RegionId"]))

    return True  # num_outlets == 2
