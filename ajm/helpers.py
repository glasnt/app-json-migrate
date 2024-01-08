import click

def warning_text(text): 
    
    click.secho("WARNING: ", fg='yellow', bold=True, nl=False)
    click.echo(text)


def success_text(text):
    click.echo(f"✅ {text}\n") 