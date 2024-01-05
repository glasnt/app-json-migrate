from jinja2 import Environment, FileSystemLoader
environment = Environment(loader=FileSystemLoader("ajm/templates/"))
template = environment.get_template("cloudbuild.yaml.tmpl")


def generate_cloudbuildyaml(settings):
    settings["region"] = "us-central1" # TODO: make dynamic. 

    content = template.render(**settings)

    # pyyaml loses comments https://github.com/yaml/pyyaml/issues/90
    # more correct validation would be this method, but we lose fidelity. 
    #validate = yaml.safe_load(content)
    #return yaml.dump(validate, sort_keys=False)

    validate = "\n".join(item for item in content.split('\n') if item.strip())
    return validate