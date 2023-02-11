"""

Ripped examples from:
 https://kitware.github.io/vtk-examples/site/Python/IO/ReadSTL/
 https://stackoverflow.com/questions/31075569/vtk-rotate-actor-programmatically-while-vtkrenderwindowinteractor-is-active
"""

import importlib
from functools import partial
import sys
import os
from os.path import dirname, basename, join
import cadquery as cq
# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkCylinderSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtkmodules.vtkIOGeometry import vtkSTLReader

class Viewer:
    def __init__(self, model_pyfile:str, cq_model, config:dict):
        self.model_pyfile = model_pyfile
        self.cq_model = cq_model
        self.config = config
        self._colors = vtkNamedColors()
        self._model_name = basename(model_pyfile).split('.py', 1)[0]
        self._stl_name = join(config['out_dir'], self._model_name + '.stl')
        self._actor = None
        self._mtime = os.stat(model_pyfile).st_mtime
        self._ren = vtkRenderer()
        self._renWin = vtkRenderWindow()
        self._renWin.AddRenderer(self._ren)
        self._renWin.SetWindowName(self._model_name)
        self._iren = vtkRenderWindowInteractor()
        self._iren.SetRenderWindow(self._renWin)
        self._ren.SetBackground(self._colors.GetColor3d('DarkOliveGreen'))

    def create_actor(self):
        reader = vtkSTLReader()
        reader.SetFileName(self._stl_name)

        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetDiffuse(0.8)
        actor.GetProperty().SetDiffuseColor(self._colors.GetColor3d('LightSteelBlue'))
        actor.GetProperty().SetSpecular(0.3)
        actor.GetProperty().SetSpecularPower(60.0)

        return actor

    def maybe_reload_model(self, *args):
        mtime = os.stat(self.model_pyfile).st_mtime
        if mtime != self._mtime:
            print("Reload...")
            self._mtime = mtime

            # Time will go by, flash window empty for the duration
            self._ren.RemoveActor(self._actor)
            self._renWin.Render()

            new_model = importlib.reload(self.cq_model)
            cq.exporters.export(new_model.instance(), self._stl_name)

            actor = self.create_actor()
            self._ren.AddActor(actor)
            self._renWin.Render()
            self._actor = actor


    def view(self) -> None:
        self._actor = self.create_actor()

        # Assign actor to the renderer
        self._ren.AddActor(self._actor)

        # Enable user interface interactor
        self._iren.Initialize()
        self._renWin.Render()

        self._iren.CreateRepeatingTimer(1000)
        self._iren.AddObserver("TimerEvent",
                               self.maybe_reload_model)
        self._iren.Start()
