from ajm.parse import parse_appjson
from ajm.generate import generate_cloudbuildyaml
import click

@click.command()
@click.argument("json_file", type=click.Path(exists=True))
def cli(json_file):
    json_fn = click.format_filename(json_file)
    settings = parse_appjson(json_fn)
    content = generate_cloudbuildyaml(settings)
    print(content)

