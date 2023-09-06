"""CadQuery model renderer"""

import argparse
import importlib
import sys
from os.path import basename, dirname, join, expanduser
from . import view
from . import prepare

def main():
    p = argparse.ArgumentParser()
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

    model_modulename = basename(a.model).split('.py', 1)[0]

    sys.path.insert(0, dirname(a.model))
    model = importlib.import_module(model_modulename)  # proves it can be done

    view.ModelVisualizer(a.model, model_modulename, conf).run_sync()

if __name__ == '__main__':
    main()
