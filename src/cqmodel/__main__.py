"""CadQuery model renderer"""

import argparse
import importlib
import sys
from os.path import basename, dirname, join, expanduser
from . import view
from . import prepare

def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', help="What to do?", choices=['show','view','use'])
    p.add_argument('model', help="Python CadQuery model file.py")
    p.add_argument('--config', '--configuration', '--configure',
                   '-c', type=str, default=None)
    a = p.parse_args()

    if a.config:
        fn = a.config
        with open(fn, 'r') as f:
            conf = json.load(f)
    else:
        conf = {
            'out_dir': dirname(a.model),
            'out_basename': basename(a.model)
        }
        try:
            fn = join(dirname(a.model), "cqmodel.conf")
            with open(fn, 'r') as f:
                conf.update(json.load(f))
        except OSError:
            try:
                fn = expanduser("~/.cqmodel.conf")
                with open(fn, 'r') as f:
                    conf.update(json.load(f))
            except OSError:
                pass
    # except error with json: complain

    model_name = basename(a.model).split('.py', 1)[0]

    sys.path.insert(0, dirname(a.model))
    instance = importlib.import_module(model_name).instance()
    sys.path.pop(0)

    if a.action == 'use':
        prepare.open_in_slicer(a.model, instance, conf)
    elif a.action in ['show', 'view']:
        view.cq_in_window(a.model, instance, conf)

if __name__ == '__main__':
    main()
