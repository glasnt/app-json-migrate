import click
import tomllib

def warning_text(text): 
    
    click.secho("WARNING: ", fg='yellow', bold=True, nl=False)
    click.echo(text)


def success_text(text):
    click.echo(f"✅ {text}\n") 

def debug_text(text): 
    click.echo(f"🪲 - {text}")

def tfvars(config_file, value): 
    # .tfvars file formats aren't toml files,
    # but we aren't using complex variables, so the parser still works.
    with open(config_file, "rb") as f:
        data = tomllib.load(f)
        return data[value]