from textwrap import dedent
from .helpers import warning_text, success_text

from jinja2 import Environment, FileSystemLoader

CLOUDBUILD_CONFIG = "_cloudbuild.yaml"
TFVARS_CONFIG = "_config.tfvars"

environment = Environment(loader=FileSystemLoader("ajm/templates/"))
template = environment.get_template("cloudbuild.yaml.tmpl")


def generate_cloudbuildyaml(settings):
    settings["region"] = "us-central1"  # TODO: make dynamic.

    content = template.render(**settings)

    # pyyaml loses comments https://github.com/yaml/pyyaml/issues/90
    # more correct validation would be this method, but we lose fidelity.
    # validate = yaml.safe_load(content)
    # return yaml.dump(validate, sort_keys=False)

    validate = "\n".join(item for item in content.split("\n") if item.strip())

    open(CLOUDBUILD_CONFIG, "w").write(validate)
    success_text(f"Wrote Cloud Build config to {CLOUDBUILD_CONFIG}")


def generate_tfvars(repo, region):
    tfvars = dedent(
        f"""
        github_repo = "{repo}"
        region = "{region}"
        cloudbuild_file = "{CLOUDBUILD_CONFIG}"

        # Generate at https://github.com/settings/tokens/new
        # Use Classic Topken with repo and read:user permissions"
        github_token = ""
        
        # ID from "Cloud Build" app on https://github.com/settings/installations
        installation_id = 
    """
    )

    warning_text(
        f"Update the github_token and installation_id values in {TFVARS_CONFIG}"
    )

    open(TFVARS_CONFIG, "w").write(tfvars)
    success_text(f"Wrote Terraform variables to {TFVARS_CONFIG}")
