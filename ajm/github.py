from github import Github, UnknownObjectException, GithubException
import os
import json
from urllib.parse import urlparse
from github import Auth


g = Github(auth=Auth.Token(os.environ.get("GITHUB_TOKEN")))

def _parse_url(github_url): 
    url = urlparse(github_url)

    repo_slug = "/".join(url.path.split("/")[1:3])
    repo = g.get_repo(repo_slug)
    directory = "/" # TODO

    return repo, directory


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
    repo, directory = _parse_url(github_url)
    branch = "main" # TODO get branch from URL or defaults

    appjson = _get_file(repo, branch, directory + "app.json")
    dockerfile = _get_file(repo, branch, directory + "Dockerfile")
    
    #pomxml = _get_file(repo, branch, "pom.xml") #TODO pomxml config

    if appjson:
        data = json.loads(appjson)
    else:
        data = {}

    if dockerfile: 
        data["_dockerfile"] = True

    data["_directory"] = directory

    return data


    




    