from ajm.parse import parse_appjson
from ajm.generate import generate_cloudbuildyaml
from ajm.github import parse_repo
import click

@click.command()
@click.argument("github_url")
def cli(github_url):
    config = parse_repo(github_url)
    settings = parse_appjson(config)
    content = generate_cloudbuildyaml(settings)
    print(content)

