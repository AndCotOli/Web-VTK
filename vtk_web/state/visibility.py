"""Visibility state changes."""
from plotter import plotter


def initialize(server):
    """Initialize visibility state."""
    state, ctrl = server.state, server.controller

    @state.change("mesh_visibility")
    def mesh_visibility_change(mesh_visibility, **kwargs):
        """Toggle visibility of the mesh edges."""
        mesh_actor = get_actor("mesh")
        if mesh_actor:
            mesh_actor.prop.show_edges = mesh_visibility
            ctrl.view_update()

    @state.change("normals_visibility")
    def normals_visibility_change(normals_visibility, **kwargs):
        """Toggle visibility of the normals."""
        normals_actor = get_actor("normals")
        if normals_actor:
            normals_actor.SetVisibility(normals_visibility)
            ctrl.view_update()


def get_actor(actor_name):
    """Get an actor from the plotter."""
    return (plotter.actors[actor_name]
            if actor_name in plotter.actors.keys()
            else None)
