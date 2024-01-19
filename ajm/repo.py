import json
import os
from urllib.parse import urlparse
from pathlib import Path

import github

if "GITHUB_TOKEN" in os.environ.keys(): 
    g = github.Github(auth=github.Auth.Token(os.environ["GITHUB_TOKEN"]))
else:
    g = github.Github()


def _parse_url(github_url):
    url = urlparse(github_url)

    path_segments = list(filter(None, url.path.split("/")))
    repo_slug = "/".join(path_segments[0:2])
    repo = g.get_repo(repo_slug)

    if len(path_segments) > 4:
        branch = "/".join(path_segments[3:4])
        directory = "/".join(path_segments[4:])
    else:
        branch = repo.default_branch
        directory = "."

    return repo, branch, directory


def _get_file(repo, branch, object_path):
    try:
        content = repo.get_contents(str(object_path), branch)
        return content.decoded_content.decode()
    except (github.UnknownObjectException, github.GithubException):
        return False


def parse_repo(github_url):
    repo, branch, directory = _parse_url(github_url)

    appjson = _get_file(repo, branch, Path(directory) / "app.json")
    dockerfile = _get_file(repo, branch, Path(directory) / "Dockerfile")
    pomxml = _get_file(repo, branch, Path(directory) / "pom.xml" )

    if appjson:
        data = json.loads(appjson)
    else:
        data = {}

    # Give parser additional context
    if dockerfile:
        data["_dockerfile"] = True
    
    if pomxml: 
        data["_pomxml"] = True


    data["_directory"] = directory
    data["_repo"] = repo.full_name
    data["_branch"] = branch
    data["_service_name"] = f'{repo.full_name.split("/")[-1]}--{data["_branch"]}--{data["_directory"]}'

    return data
