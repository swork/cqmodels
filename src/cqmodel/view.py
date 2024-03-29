"""

Ripped examples from:
 https://kitware.github.io/vtk-examples/site/Python/IO/ReadSTL/
 https://stackoverflow.com/questions/31075569/vtk-rotate-actor-programmatically-while-vtkrenderwindowinteractor-is-active
"""

import multiprocessing as mp
import importlib
import traceback
import time
import sys
import os
from functools import partial
from os.path import dirname, basename, join
import cadquery as cq
from .viewer import view_stl

class ModelVisualizer:
    """Writes .stl for each item in a CadQuery model, and repeats on input changes."""

    def __init__(self, model_pyfile:str, model_modulenameXXX:str, config:dict):
        """
        model_modulename is ignored, prep to calc it by convention
        """
        self.mp_context = mp.get_context('spawn')
        self.model_pyfile = model_pyfile
        self.config = config

        self.model_modulename = basename(model_pyfile).split('.py', 1)[0]
        if dirname(model_pyfile) not in sys.path:
            sys.path.insert(0, dirname(model_pyfile))
        self.model_module = importlib.import_module(self.model_modulename)
        self._mtime = os.stat(model_pyfile).st_mtime
        self._viewers = {}

    def __del__(self):
        for viewer in self._viewers.keys():
            self._viewers[viewer].terminate()  # die while leaving .stl in place
            self._viewers[viewer].join()  # wait for it to finish dying. Why? Zombies?

    def _calc_model(self, callable, stls, stl_filename):
        try:
            model = callable()
        except Exception as e:
            print(f'Trouble with model "{stl_filename.split(".", 1)[0]}"')
            traceback.print_exception(e)
            try:
                stls.remove(stl_filename)
            except KeyError:
                pass
            return None
        stls.add(stl_filename)
        return model


    def write_stls(self):
        """Re-import model, write out stl files, and return an iterable of their names"""
        self.model_module = importlib.reload(self.model_module)
        stls = set()
        if getattr(self.model_module, 'instance', None):
            stl_filename = self.model_pyfile.replace(".py", ".stl")
            call_to_compute = self.model_module.instance
            model = self._calc_model(call_to_compute, stls, stl_filename)
            if model:
                cq.exporters.export(model, stl_filename)
            else:
                pass  # failure is presented to user by disappearance of viewer window
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
                    stl_filename = join(dirname(self.model_pyfile), f'{method_name}.stl')
                    call_to_compute = getattr(class_instance, method_name)
                else:  # "function"
                    stl_filename = join(dirname(self.model_pyfile), f'{instance}.stl')
                    call_to_compute = getattr(self.model_module, instance)
                model = self._calc_model(call_to_compute, stls, stl_filename)
                if model:
                    cq.exporters.export(model, stl_filename)
                else:
                    # Visually present failure? Yellow background? How to signal?
                    pass
        print(stls)
        return stls

    def converge_viewers(self, stls):
        """Make sure a viewer is running for each .stl file in stls, and no extras."""

        # Clean up viewers that died, maybe err'd out, maybe user killed
        for s in list(self._viewers.keys()):
            if not self._viewers[s].is_alive():
                self._viewers[s].join()
                del self._viewers[s]

        needed = stls - self._viewers.keys()
        extraneous = set(self._viewers.keys()) - stls
        for stl_file in extraneous:
            os.unlink(stl_file)  # and expect viewer to notice and exit
            self._viewers[stl_file].join()
            del self._viewers[stl_file]
        for stl_file in needed:
            if os.path.isfile(stl_file):
                p = mp.Process(target=view_stl, args=(stl_file,))
                p.start()
                self._viewers[stl_file] = p
            else:
                print(f'Expected {stl_file} but no.')

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

