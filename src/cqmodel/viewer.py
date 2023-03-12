import argparse
import sys
import os
import vtkmodules.vtkInteractionStyle
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
    def __init__(self, stl_name:str, config:dict):
        self._stl_name = stl_name
        self._config = config
        try:
            self._mtime = os.stat(self._stl_name).st_mtime
        except OSError:
            sys.exit(0)
        self._colors = vtkNamedColors()
        self._actor = None
        self._ren = vtkRenderer()
        self._renWin = vtkRenderWindow()
        self._renWin.AddRenderer(self._ren)
        self._renWin.SetWindowName(os.path.basename(self._stl_name))
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
        try:
            mtime = os.stat(self._stl_name).st_mtime
        except OSError:
            sys.exit(0)
        if mtime != self._mtime:
            print("Reload...")
            self._mtime = mtime

            # Time will go by, flash window empty for the duration
            self._ren.RemoveActor(self._actor)
            self._renWin.Render()
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

        self.maybe_reload_model()

        self._iren.CreateRepeatingTimer(100)
        self._iren.AddObserver("TimerEvent",
                               self.maybe_reload_model)
        self._iren.Start()

def view_stl(stl_file):
    Viewer(stl_file, {}).view()

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('stl_file', type=str)
    a = p.parse_args()
    view_stl(a.stl_file)
