"""

Ripped examples from:
 https://kitware.github.io/vtk-examples/site/Python/IO/ReadSTL/
 https://stackoverflow.com/questions/31075569/vtk-rotate-actor-programmatically-while-vtkrenderwindowinteractor-is-active
"""

import multiprocessing as mp
import importlib
import time
import sys
import os
from functools import partial
from os.path import dirname, basename, join
import cadquery as cq
from .viewer import view_stl

class ModelVisualizer:
    """Writes .stl for each item in a CadQuery model, and repeats on input changes."""

    def __init__(self, model_pyfile:str, model_modulename, config:dict):
        self.mp_context = mp.get_context('spawn')
        self.model_pyfile = model_pyfile
        self.model_modulename = model_modulename
        self.config = config
        self.model_module = importlib.import_module(model_modulename)
        self._mtime = os.stat(model_pyfile).st_mtime
        self._viewers = {}

    def __del__(self):
        for viewer in self._viewers.keys():
            self._viewers[viewer].terminate()  # die while leaving .stl in place
            self._viewers[viewer].join()  # wait for it to finish dying. Why? Zombies?

    def write_stls(self):
        """Re-import model, write out stl files, and return an iterable of their names"""
        self.model_module = importlib.reload(self.model_module)
        stls = set()
        if getattr(self.model_module, 'instance', None):
            stl_filename = self.model_pyfile.replace(".py", ".stl")
            model = self.model_module.instance()
            cq.exporters.export(model, stl_filename)
            stls.add(stl_filename)
        elif getattr(self.model_module, 'instances'):
            class_instances = {}
            stls = set()
            for instance in self.model_module.instances():
                if '.' in instance:  # "class.method"
                    cls_name, method_name = instance.split('.', 1)
                    if cls_name in class_instances:
                        class_instance = class_instances[cls_name]
                    else:
                        class_instance = getattr(self.model_module, cls_name)()
                        class_instances[cls_name] = class_instance
                    bound_method = getattr(class_instance, method_name)
                    model = bound_method()  # call class.method()
                    stl_filename = join(dirname(self.model_pyfile), f'{method_name}.stl')
                else:  # "function"
                    model = getattr(self.model_module, instance)()  # call instance()
                    stl_filename = join(dirname(self.model_pyfile), f'{instance}.stl')
                cq.exporters.export(model, stl_filename)
                stls.add(stl_filename)
        return stls

    def converge_viewers(self, stls):
        """Make sure a viewer is running for each .stl file in stls, and no extras."""
        needed = stls - self._viewers.keys()
        extraneous = set(self._viewers.keys()) - stls
        for stl_file in extraneous:
            os.unlink(stl_file)  # and expect viewer to notice and exit
            self._viewers[stl_file].join()
            del self._viewers[stl_file]
        for stl_file in needed:
            p = mp.Process(target=view_stl, args=(stl_file,))
            p.start()
            self._viewers[stl_file] = p

    def run_sync(self):
        while True:
            new_filenames = self.write_stls()
            self.converge_viewers(new_filenames)
            while True:
                time.sleep(0.1)
                new_mtime = os.stat(self.model_pyfile).st_mtime
                if new_mtime != self._mtime:
                    self._mtime = new_mtime
                    break

    async def run_async(self):
        while True:
            new_filenames = self.write_stls()
            self.converge_viewers(new_filenames)
            while True:
                await anyio.sleep(0.1)
                new_mtime = os.state(self.model_pyfile).st_mtime
                if new_mtime != self._mtime:
                    self._mtime = new_mtime
                    break

