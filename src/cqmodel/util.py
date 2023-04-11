import cadquery as cq

def init_params(model, updates):
    """Transmogrify model's .params dict into individual attributes.

    Spaces in .params keys get made into underscores.

    updates supplies value overrides, applied as the new attributes.
    """
    for param in model.params.keys():
        param_attrname = param.replace(' ', '_')
        if param in updates:  # with spaces not underscores
            setattr(model, param_attrname, updates[param])
            del updates[param]
        elif param_attrname in updates:
            setattr(model, param_attrname, updates[param_attrname])
            del updates[param_attrname]
        else:
            setattr(model, param_attrname, model.params[param])
    if updates:
        raise RuntimeError(f"Bogus parameter overrides: {join(',', updates.keys())}")

def infoize():
    """Monkeypatch in the info str() fns from primer.html in CQ docs"""

    def tidy_repr(obj):
        """ Shortens a default repr string
        """
        return repr(obj).split('.')[-1].rstrip('>')

    def _ctx_str(self):
        return (
            tidy_repr(self) + ":\n"
            + f"    pendingWires: {self.pendingWires}\n"
            + f"    pendingEdges: {self.pendingEdges}\n"
            + f"    tags: {self.tags}"
        )
    cq.cq.CQContext.__str__ = _ctx_str

    def _wp_str(self):
        out = tidy_repr(self) + ":\n"
        out += f"  parent: {tidy_repr(self.parent)}\n" if self.parent else "  no parent\n"
        out += f"  plane: {self.plane}\n"
        out += f"  objects: {self.objects}\n"
        out += f"  modelling context: {self.ctx}"
        return out
    cq.Workplane.__str__ = _wp_str
