from collections import defaultdict
from functools import partial
from importlib import import_module
from importlib.util import find_spec
from pkgutil import iter_modules
from typing import DefaultDict, Set

from typing_extensions import TypedDict


class TypeDict(TypedDict):
    classes: Set[str]
    functions: Set[str]
    enums: Set[str]
    other: Set[str]


def _ispublic(name):
    return not name.startswith("_")


def new_type_dict() -> TypeDict:
    return TypeDict(
        {"classes": set(), "functions": set(), "enums": set(), "other": set()}
    )


PKGS: DefaultDict[str, DefaultDict[str, TypeDict]] = DefaultDict(
    partial(DefaultDict, dict)
)
for pkg in {"PyQt5", "PyQt6", "PySide2", "PySide6"}:
    spec = find_spec(pkg)
    for mod in iter_modules(spec.submodule_search_locations):
        submod = import_module(f"{pkg}.{mod.name}")
        PKGS[pkg][mod.name] = submod.__dict__
        # d = new_type_dict()
        # for name, v in submod.__dict__.items():
        #     if not _ispublic(name):
        #         continue
        #     if isinstance(v, FunctionType):
        #         d["functions"].add(name)
        #     elif isinstance(v, (int, EnumMeta)):
        #         d["enums"].add(name)
        #     elif isinstance(v, type):
        #         d["classes"].add(name)
        #     else:
        #         d["other"].add(name)
        #     PKGS[pkg][mod.name] = d


INTERSECTION = defaultdict(dict)
for mod in list(PKGS["PyQt6"]):
    if common_clsnames := set.intersection(*(set(pkg[mod]) for pkg in PKGS.values())):
        for clsname in common_clsnames:
            if attrs := set.intersection(
                *(set(pkg[mod][clsname]) for pkg in PKGS.values())
            ):
                INTERSECTION[mod][clsname] = attrs

UNION = defaultdict(dict)
for mod in list(PKGS["PyQt6"]):
    if common_clsnames := set.union(*(set(pkg[mod]) for pkg in PKGS.values())):
        for clsname in common_clsnames:
            d = (set(pkg[mod][clsname]) for pkg in PKGS.values() if clsname in pkg[mod])
            if attrs := set.union(*d):
                UNION[mod][clsname] = attrs

DIFFERENCE = defaultdict(dict)
for mod in list(UNION):
    if clsdiffs := set(UNION[mod]).difference(INTERSECTION[mod]):
        for clsname in clsdiffs:
            if attrs := (
                set(UNION[mod][clsname]).difference(INTERSECTION[mod][clsname])
                if clsname in INTERSECTION[mod]
                else UNION[mod][clsname]
            ):
                DIFFERENCE[mod][clsname] = attrs

PKGDIFF = defaultdict(partial(defaultdict, dict))
for pkg, mods in PKGS.items():
    for mod, classnames in mods.items():
        for classname, attrs in classnames.items():
            if diff := (
                attrs.difference(INTERSECTION[mod][classname])
                if classname in INTERSECTION[mod]
                else attrs
            ):
                PKGDIFF[pkg][mod][classname] = diff
