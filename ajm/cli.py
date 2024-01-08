from ajm.parse import parse_appjson
from ajm.generate import generate_cloudbuildyaml, generate_tfvars
from ajm.repo import parse_repo
import click


CLOUDBUILD_CONFIG = "_cloudbuild.yaml"
TFVARS_CONFIG = "_config.tfvars"

@click.group()
@click.version_option()
def cli():
    pass


@cli.command(name="generate")
@click.argument("github_url")
@click.argument("region", default="us-central1")
def generate(github_url, region):
    config = parse_repo(github_url)
    settings = parse_appjson(config)
    generate_cloudbuildyaml(settings)
    generate_tfvars(config["_repo"], region)
    click.echo("Address warnings, then run apply: ")
    click.echo("python main.py apply")
    

@cli.command(name="apply")
def apply():
    # TODO: get REGION from tfvars
    print("terraform import google_artifact_registry_repository.default us-central1/cloud-run-source-deploy")
    print(f"terraform apply -var-file={TFVARS_CONFIG}")
