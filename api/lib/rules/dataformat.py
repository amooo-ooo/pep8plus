import json
f_input = "ruff"

with open(f_input + ".json", "r") as f:
    rules = json.loads(f.read())

if f_input == "flake8":
    with open("ruff.json", "r") as f:
        ruff = json.loads(f.read())

    ruff_rules = {}
    for category, rule in ruff.items():
        for code, actual in rule.items():
            ruff_rules[code] = actual | {"category": category}

n_rules = {}
for category, rule in rules.items():
    for code, actual in rule.items():
        if f_input == "flake8":
            try:
                n_rules[code] = {"name": ruff_rules[code]["name"], "description": actual["name"], "category": category, "value": True}
            except:
                n_rules[code] = {"name": "UNDEFINED", "description": actual["name"], "category": category, "value": True}
                print(code)
        else:
            n_rules[code] = actual | {"category": category}


with open(f_input + "_new.json", "w") as f:
    f.write(json.dumps(n_rules))
 