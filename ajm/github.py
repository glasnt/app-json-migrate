from github import Github, UnknownObjectException, GithubException
import os
import json
from urllib.parse import urlparse


g = Github()


def _parse_url(github_url):
    url = urlparse(github_url)

    path_segments = url.path.split("/")
    repo_slug = "/".join(path_segments[1:3])
    repo = g.get_repo(repo_slug)

    if len(path_segments) > 2:
        branch = "/".join(path_segments[3:5])
        directory = "/".join(path_segments[5:])
    else:
        branch = repo.default_branch
        directory = "/"

    return repo, branch, directory


def object_exists(repo, branch, object_path):
    try:
        repo.get_contents(object_path, branch)
        return True
    except (UnknownObjectException, GithubException):
        return False


def _get_file(repo, branch, object_path):
    try:
        content = repo.get_contents(object_path, branch)
        return content.decoded_content.decode()
    except (UnknownObjectException, GithubException):
        return False


def parse_repo(github_url):
    repo, branch, directory = _parse_url(github_url)

    appjson = _get_file(repo, branch, directory + "app.json")
    dockerfile = _get_file(repo, branch, directory + "Dockerfile")

    # TODO: jib/pom.xml config

    if appjson:
        data = json.loads(appjson)
    else:
        data = {}

    # Give parser additional context
    if dockerfile:
        data["_dockerfile"] = True

    data["_directory"] = directory
    data["_repo"] = repo.full_name
    data["_service_name"] = repo.full_name.split("/")[-1]

    return data
