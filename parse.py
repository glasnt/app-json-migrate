import json

def parse_appjson(json_fn): 

    data = json.load(open(json_fn))

    settings = {}

    settings["buildpacks"] = "test"

    return settings