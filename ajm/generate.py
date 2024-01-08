from textwrap import dedent
from .helpers import warning_text, success_text, debug_text
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

CLOUDBUILD_CONFIG = "_cloudbuild.yaml"
TFVARS_CONFIG = "_config.tfvars"

environment = Environment(loader=FileSystemLoader("ajm/templates/"))
template = environment.get_template("cloudbuild.yaml.tmpl")


def generate_cloudbuildyaml(settings):
    content = template.render(**settings)

    # pyyaml loses comments https://github.com/yaml/pyyaml/issues/90
    # more correct validation would be this method, but we lose fidelity.
    # 
    # validate = yaml.safe_load(content)
    # return yaml.dump(validate, sort_keys=False)

    validate = "\n".join(item for item in content.split("\n") if item.strip())

    open(CLOUDBUILD_CONFIG, "w").write(validate)
    success_text(f"Wrote Cloud Build config to {CLOUDBUILD_CONFIG}")


def generate_tfvars(config):
    tfvars = dedent(
        f"""
        github_repo = "{config['_repo']}"
        git_default_branch = "{config['_branch']}"
        region = "{config['_region']}"
        cloudbuild_file = "{CLOUDBUILD_CONFIG}"

        # Generate at https://github.com/settings/tokens/new
        # Use Classic Token with repo and read:user permissions"
        github_token = ""
        
        # ID from "Cloud Build" app on https://github.com/settings/installations
        installation_id = 
    """
    )

    if not Path(TFVARS_CONFIG).exists(): 

        open(TFVARS_CONFIG, "w").write(tfvars)
        success_text(f"Wrote Terraform variables to {TFVARS_CONFIG}")

        warning_text(
            f"Update the github_token and installation_id values in {TFVARS_CONFIG}"
        )

    else: 
        debug_text(f"Using existing {TFVARS_CONFIG}.")
