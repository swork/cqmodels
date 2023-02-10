import sys
from os.path import dirname, basename, join
import subprocess
import cadquery as cq

def open_in_slicer(model_pyfile:str, cq_instance, config:dict) -> None:
    """Render CQ model into BambuStudio"""

    model_name = basename(model_pyfile).split('.py', 1)[0]
    out_name = join(config['out_dir'], model_name + '.step')
    cq.exporters.export(cq_instance, out_name)

    # subprocess.check_call(['open', out_name])

    # Output on screen includes outfile on last line

