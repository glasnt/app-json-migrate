from ajm.parse import parse_appjson
from ajm.generate import generate_cloudbuildyaml, generate_tfvars
from ajm.repo import parse_repo
import click

@click.group()
@click.version_option()
def cli():
    pass
    

@cli.command(name="generate")
@click.argument("github_url")
def generate(github_url):
    config = parse_repo(github_url)
    settings = parse_appjson(config)
    content = generate_cloudbuildyaml(settings)

    open("_cloudbuild.yaml", "w").write(content)

    tfvars = generate_tfvars(config["_repo"])
    open("_config.tfvars", "w").write(tfvars)



@cli.command(name="apply")
def apply():
    print("Apply command")