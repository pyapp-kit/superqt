from . import _submodule

_mdl, _names = _submodule(__name__.split(".")[-1])
globals().update({k: getattr(_mdl, k) for k in _names})
