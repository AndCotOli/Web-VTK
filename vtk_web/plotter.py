"""Plotter Set Up."""
import pyvista as pv

pv.OFF_SCREEN = True

plotter = pv.Plotter()

airplane = pv.read("airplane.vtk")
plotter.add_mesh(airplane, name="mesh")
