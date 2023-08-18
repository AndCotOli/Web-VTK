"""Visibility state changes."""
from plotter import plotter


def initialize(server):
    """Initialize visibility state."""
    state, ctrl = server.state, server.controller

    @state.change("mesh_visibility")
    def mesh_visibility_change(mesh_visibility, **kwargs):
        """Toggle visibility the of mesh edges."""
        mesh_actor = plotter.actors["mesh"]
        if mesh_actor:
            mesh_actor.prop.show_edges = mesh_visibility
            ctrl.view_update()
