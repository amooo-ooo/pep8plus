import json
f_input = ["ruff", "flake8", "pylint"]

for file in f_input:
    with open(file + ".json", "r") as f:
        rules = json.loads(f.read())

    grammered = {}
    for key, values in rules.items():
        desc = values["description"]
        grammered[key] = values | {"description": desc[0].upper() + (desc[1:] if desc.endswith(".") else desc[1:] + ".")}


    with open(file + ".json", "w") as f:
        f.write(json.dumps(grammered))