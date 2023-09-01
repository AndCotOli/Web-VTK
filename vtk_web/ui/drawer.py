"""Drawer UI."""
from trame.widgets import vuetify


def initialize(layout, server):
    """Set up drawer layout."""
    state, ctrl = server.state, server.controller
    with layout.drawer:
        render_controls(ctrl)
        vuetify.VDivider()
        visibility_controls()
        vuetify.VDivider()
        vcs_controls(state)


def render_controls(ctrl):
    """Set up rendering controls."""
    with vuetify.VContainer(fluid=True):
        with vuetify.VBtn(click=ctrl.view_reset_camera):
            vuetify.VSubheader("Reset Camera")
        vuetify.VCheckbox(
            label="Render remotely",
            v_model=(ctrl.view_get_rendering_state(), False)
        )


def visibility_controls():
    """Set up visibility controls."""
    options = ("mesh", "normals")
    with vuetify.VContainer(fluid=True):
        for opt in options:
            vuetify.VCheckbox(
                label=f"Show {opt}",
                v_model=(f"{opt}_visibility", False)
            )


def vcs_controls(state):
    """Set up vcs controls."""
    with vuetify.VContainer(fluid=True):
        vuetify.VCheckbox(
            label="Show inlets",
            v_model=("inlet_visibility", False),
            disabled=not state.is_valid_mesh
        )
