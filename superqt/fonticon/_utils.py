def parse_icons_json(file):
    import json

    with open(file) as f:
        icons = json.load(f)
    return {
        k: {
            "unicode": v["unicode"],
            "label": v["label"],
            "svg": v["svg"]["brands"]["raw"],
        }
        for k, v in icons.items()
        if "brands" in v["styles"]
    }
