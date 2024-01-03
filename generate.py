import yaml


from jinja2 import Environment, FileSystemLoader
environment = Environment(loader=FileSystemLoader("templates/"))
template = environment.get_template("cloudbuild.yaml.tmpl")


def generate_cloudbuildyaml(settings):
    content = template.render(**settings)
    validate = yaml.safe_load(content)
    return yaml.dump(validate, sort_keys=False)