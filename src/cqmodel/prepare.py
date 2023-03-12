import sys
from os.path import dirname, basename, join
import subprocess
import importlib
import cadquery as cq

def open_in_slicer(model_pyfile:str, model_modulename, config:dict) -> None:
    """Render CQ model into BambuStudio"""

    model = importlib.import_module(model_modulename)

    model_name = basename(model_pyfile).split('.py', 1)[0]
    out_name = join(config['out_dir'], model_name + '.step')
    cq.exporters.export(cq_instance, out_name)

    # subprocess.check_call(['open', out_name])

    # Output on screen includes outfile on last line

