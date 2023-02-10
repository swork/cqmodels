import importlib
import sys
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

def cq_in_window(model_pyfile:str, cq_instance, config:dict) -> None:
    model_name = basename(model_pyfile).split('.py', 1)[0]
    stl_name = join(config['out_dir'], model_name + '.stl')
    cq.exporters.export(cq_instance, stl_name)

    # https://kitware.github.io/vtk-examples/site/Python/IO/ReadSTL/
    colors = vtkNamedColors()

    reader = vtkSTLReader()
    reader.SetFileName(stl_name)

    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetDiffuse(0.8)
    actor.GetProperty().SetDiffuseColor(colors.GetColor3d('LightSteelBlue'))
    actor.GetProperty().SetSpecular(0.3)
    actor.GetProperty().SetSpecularPower(60.0)

    # Create a rendering window and renderer
    ren = vtkRenderer()
    renWin = vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.SetWindowName('ReadSTL')

    # Create a renderwindowinteractor
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # Assign actor to the renderer
    ren.AddActor(actor)
    ren.SetBackground(colors.GetColor3d('DarkOliveGreen'))

    # Enable user interface interactor
    iren.Initialize()
    renWin.Render()
    iren.Start()
    # __doc__: -- and the path to watching the input for auto-reload:
    # 'Start(self) -> None\nC++: virtual void Start()\n\nStart the event loop.
    # This is provided so that you do not have to\nimplement your own event
    # loop. You still can use your own event\nloop if you want.\n'
