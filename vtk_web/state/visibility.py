"""Visibility state changes."""
from plotter import plotter


def initialize(server):
    """Initialize visibility state."""
    state, ctrl = server.state, server.controller

    @state.change("mesh_visibility")
    def mesh_visibility_change(mesh_visibility, **kwargs):
        """Toggle visibility of the mesh edges."""
        mesh_actor = plotter.actors["mesh"] if "mesh" in plotter.actors.keys() else None
        if mesh_actor:
            mesh_actor.prop.show_edges = mesh_visibility
            ctrl.view_update()

    @state.change("normals_visibility")
    def normals_visibility_change(normals_visibility, **kwargs):
        """Toggle visibility of the normals."""
        normals_actor = plotter.actors["normals"] if "normals" in plotter.actors.keys() else None
        if normals_actor:
            normals_actor.SetVisibility(normals_visibility)
            ctrl.view_update()
