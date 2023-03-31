
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
