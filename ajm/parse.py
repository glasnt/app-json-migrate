from pathlib import Path


def _parse_options(options):
    _settings = {}

    # Parse all stringy options
    for config in ["memory", "cpu", "concurrency", "max-instances", "port"]:
        if config in options.keys():
            _settings[config] = f"--{config}={options[config]}"

    if (
        "allow-unauthenticated" in options.keys()
        and options["allow-unauthenticated"] is False
    ):
        _settings["authentication"] = "--no-allow-authenticated"
    else:
        _settings["authentication"] = "--allow-authenticated"

    if "http2" in options.keys() and options["http2"] is True:
        _settings["http2"] = "--use-http2"


    return _settings


def _parse_hooks(hooks):
    _settings = {}

    for hook in ["prebuild", "postbuild", "precreate", "postcreate"]:
        if hook in hooks.keys() and hooks[hook] is not None:
            command = "; ".join(hooks[hook]["commands"])
            _settings[hook] = command

    return _settings

def _parse_env(env): 

    """
    { "TITLE": { "description": "title for your site" }}


    - id: update service
    args:
        - update
        - $_SERVICE_NAME
        - --set-env-vars=TITLE=${_TITLE}

    substitutions: 
        _TITLE: "" # title for your site
    """

    _service_envs = []
    _service_secrets = []
    _extra_substitutions = []

    for key in env:
        # Shortcut generated values
        if "generator" in env[key].keys() and env[key]["generator"] == "secret":
            _service_secrets.append(f"{key}={key}:latest")

        else: 
        
            substitution = f"    _{key}: "
            if "value" in env[key].keys(): 
                substitution += '"' + env[key]["value"] + '"'
            elif "generator" in  env[key].keys() and env[key]["generator"] == "secret":
                substitution += '""  # GENERATOR'
            else: 
                substitution += '""'
            
            if "description" in env[key].keys(): 
                substitution += f"  # {env[key]['description']}"

            _service_envs.append( key + "=${_" + key + "}") #TODO literal braces in f-strings how
            _extra_substitutions.append(substitution)

    _set_envvars, _set_secrets = "", ""
    if len(_service_envs) > 0: 
        _set_envvars = "- --set-env-vars=" + ",".join(_service_envs)
    if len(_service_secrets) > 0: 
        _set_secrets = "- --set-secrets=" + ",".join(_service_secrets)

    return _extra_substitutions, _set_envvars, _set_secrets
    


def parse_appjson(data):

    settings = {}
    
    # Parse name
    if "name" in data.keys():
        settings["service_name"] = data["name"]
    else:
        settings["service_name"] = "my-service"  # TODO: generate based on repo name.

    # Added by parse_repo()
    if "_directory" in data.keys(): 
        if data["_directory"] == "/": 
            settings["dockerfile_location"] = "- Dockerfile"
        else: 
            settings["context_directory"] = f'- -f={data["_directory"]}'
            settings["dockerfile_location"] = f'- {Path(data["_directory"], "Dockerfile")}'

    # Parse env 
    if "env" in data.keys(): 
        extra_substitutions, settings["service_envs"], settings["service_secrets"],  = _parse_env(data["env"])
        settings["extra_substitutions"] = "\n".join(extra_substitutions)

    # Parse Dockerfile (key added by parse_repo())
    if "_dockerfile" in data.keys(): 
        settings["buildpacks"] = False

    # Parse builder
    if "build" in data.keys(): 
        if "skip" in data["build"].keys() and data["build"]["skip"] is True: 
            settings["skip_build"] = True
        if "buildpacks" in data["build"].keys():
            settings["buildpacks"] = True

            if "builder" in data["build"]["buildpacks"].keys(): 
                settings["buildpacks_builder"] = data["build"]["buildpacks"]["builder"] 
            
            if "buildpacks_builder" not in settings.keys(): 
                settings["buildpacks_builder"] = "gcr.io/buildpacks/builder:v1"

    # Parse options
    options = {}
    if "options" in data.keys():
        options = _parse_options(data["options"])

    if "authentication" not in options.keys():
        options = {"authentication": "--allow-unauthenticated"}
    settings["options"] = "\n      - ".join(options.values())

    # Parse hooks
    if "hooks" in data.keys():
        settings.update(_parse_hooks(data["hooks"]))

    return settings
