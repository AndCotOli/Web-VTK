"""Drawer UI."""
from trame.widgets import vuetify


def initialize(layout, ctrl):
    """Set up drawer layout."""
    with layout.drawer:
        camera_controls(ctrl)
        vuetify.VSpacer()
        visibility_controls()
        vuetify.VDivider()
        vcs_controls()


def camera_controls(ctrl):
    """Set up camera controls."""
    with vuetify.VContainer(fluid=True):
        with vuetify.VBtn(click=ctrl.view_reset_camera):
            vuetify.VSubheader("Reset Camera")


def visibility_controls():
    """Set up visibility controls."""
    options = ("mesh", "normals")
    with vuetify.VContainer(fluid=True):
        for opt in options:
            vuetify.VCheckbox(
                label=f"Show {opt}",
                v_model=(f"{opt}_visibility", False)
            )


def vcs_controls():
    """Set up vcs controls."""
    with vuetify.VContainer(fluid=True):
        vuetify.VCheckbox(
            label="Show inlets",
            v_model=("inlet_visibility", False)
        )
