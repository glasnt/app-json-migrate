from pathlib import Path

from .helpers import warning_text


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
        _settings["authentication"] = "--no-allow-unauthenticated"
    else:
        _settings["authentication"] = "--allow-unauthenticated"

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
            elif "generator" in env[key].keys() and env[key]["generator"] == "secret":
                substitution += '""  # GENERATOR'
                warning_text("Value {key} needs secret TODO")
            else:
                substitution += '""'
                warning_text("Value {key} needs default TODO")

            if "description" in env[key].keys():
                substitution += f"  # {env[key]['description']}"

            _service_envs.append(f"{key}=${{_{key}}}")
            _extra_substitutions.append(substitution)

    _set_envvars, _set_secrets = "", ""
    if len(_service_envs) > 0:
        _set_envvars = "- --set-env-vars=" + ",".join(_service_envs)
    if len(_service_secrets) > 0:
        _set_secrets = "- --set-secrets=" + ",".join(_service_secrets)

    return _extra_substitutions, _set_envvars, _set_secrets


def _fix_service_name(service_name):
    # Based on tryFixServiceName https://github.com/GoogleCloudPlatform/cloud-run-button/blob/master/cmd/cloudshell_open/cloudrun.go#L121
    service_name = service_name[:63].lower().replace("_", "-")

    if service_name[0] == "-":
        service_name = f"srv{service_name}"
    if service_name[-1] == "-":
        service_name = service_name[:-1]

    return service_name


def parse_appjson(data):
    settings = {}

    # Parse name
    if "name" in data.keys():
        settings["service_name"] = data["name"]
    else:
        settings["service_name"] = data["_service_name"]

    settings["service_name"] = _fix_service_name(settings["service_name"])
    settings["region"] = data["_region"]

    # Added by parse_repo()
    if "_directory" in data.keys():
        if data["_directory"] == "/":
            settings["dockerfile_location"] = "- Dockerfile"
        else:
            settings["context_directory"] = data["_directory"]
            settings["docker_context"] = f'- {data["_directory"]}'
            settings[
                "dockerfile_location"
            ] = f'- -f={Path(data["_directory"], "Dockerfile")}'

    # Parse env
    if "env" in data.keys():
        (
            extra_substitutions,
            settings["service_envs"],
            settings["service_secrets"],
        ) = _parse_env(data["env"])
        settings["extra_substitutions"] = "\n".join(extra_substitutions)

    # Parse build type by file
    if "_dockerfile" in data.keys():
        settings["build_type"] = "docker"
    
    if "_pomxml" in data.keys(): 
        settings["build_type"] = "jib"

    # Parse build if given
    if "build" in data.keys():
        if "skip" in data["build"].keys() and data["build"]["skip"] is True:
            settings["skip_build"] = True
        if "buildpacks" in data["build"].keys():
            settings["build_type"] = "buildpacks"

            if "builder" in data["build"]["buildpacks"].keys():
                settings["buildpacks_builder"] = data["build"]["buildpacks"]["builder"]

    # Default to buildpacks if no expected files found
    if "build_type" not in settings.keys(): 
        settings["build_type"] = "buildpacks"    

    # Provide default builder if not already provided.
    if "build_type" in settings.keys() and settings["build_type"] == "buildpacks" and "buildpacks_builder" not in settings.keys():
        settings["buildpacks_builder"] = "gcr.io/buildpacks/builder:v1"

    # Parse options
    options = {}
    if "options" in data.keys():
        options = _parse_options(data["options"])

    if "authentication" not in options.keys():
        options = {"authentication": "--allow-unauthenticated"}
    settings["options"] = "\n        - ".join(options.values()) #TODO: resilient space padding

    # Parse hooks
    if "hooks" in data.keys():
        settings.update(_parse_hooks(data["hooks"]))

    return settings
