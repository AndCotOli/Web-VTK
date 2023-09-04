#!/bin/bash
pip install /local-app
pip uninstall vtk -y
pip install --no-cache-dir --extra-index-url https://wheels.vtk.org vtk-osmesa
