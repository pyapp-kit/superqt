def ensure_identifier(name: str) -> str:
    """Normalize string to valid identifier"""
    import keyword

    if not name:
        return ""

    # add _ to beginning of names starting with numbers
    if name[0].isdigit():
        name = f"_{name}"

    # add _ to end of reserved keywords
    if keyword.iskeyword(name):
        name += "_"

    # replace dashes with underscores
    name = name.replace("-", "_")

    assert str.isidentifier(name), f"Could not canonicalize name: {name}"
    return name


def get_identifier(obj: object, name: str) -> str:
    """Given a class or namespace, find an attribute that may be canonicalized."""
    if hasattr(obj, name):
        return getattr(obj, name)

    identifier = ensure_identifier(name)
    if hasattr(obj, identifier):
        return getattr(obj, identifier)

    if name != identifier:
        identifier += f" or {name}"
    raise ValueError(f"Object {obj!r} has no member: {identifier}")
