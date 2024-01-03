import json


def _parse_options(options):
    _settings = {}

    # Parse all stringy options
    for config in ["memory", "cpu", "concurrency", "max-instances", "port"]:
        if config in options.keys(): 
            _settings[config] = f"- --{config}={options['config']}"

    if "allow-unauthenticated" in options.keys() and options["allow-unauthenticated"] is False:
        _settings["authentication"] = "- --no-allow-authenticated"
    else:
        _settings["authentication"] = "- --allow-authenticated"

    if "http2" in options.keys() and options["http2"] is True:
        _settings["http2"] = "- --use-http2"

    return _settings


def _parse_hooks(hooks):
    _settings = {}

    for hook in ["prebuild", "postbuild", "precreate", "postcreate"]:
        if hooks[hook] is not None:
            _settings[hook] = hooks[hook]

    return _settings


def parse_appjson(json_fn):
    data = json.load(open(json_fn))

    settings = {}
    settings["options"] = {}
    if "options" in data.keys(): 
        settings["options"] = _parse_options(data["options"])
    
    if "authentication" not in settings["options"].keys(): 
        settings["options"] = {"authentication": "- --allow-unauthenticated"}

    if "hooks" in data.keys(): 
        settings.update(_parse_hooks(data["hooks"]))


    return settings
