#!/usr/local/bin/python3

import os
import sys
import re
import string
from pygit2 import Repository
from github import Github, Issue
import giturlparse
import argparse

repo = Repository('.')

def ghGetOrganization(gh, name):
    try:
        return gh.get_organization(name)
    except:
        print(name, 'is not an organization. error')
        return None

def ghGetUser(gh, name):
    try:
        return gh.get_user(name)
    except:
        print(name, 'is not an user. error')
        return None

def ghGetOwner(gh, namespace):
    org = ghGetOrganization(gh, namespace)
    if org:
        return org

    user = ghGetUser(gh, namespace)
    if user and user.name == gh.get_user().name:
        print(namespace, "is authorized user")
        return gh.get_user()

def ghGetRepo(gh, owner, repoName):
    owner = ghGetOwner(gh, owner)
    if not owner:
        print("invalid owner")
        return None
    if repoName not in [r.name for r in owner.get_repos()]:
        return None
    repo = owner.get_repo(repoName)
    return repo

###----

def createpullrequest(args, gh_repo):
    parser = argparse.ArgumentParser()
    parser.add_argument('--into', help='base branch to merge into', type=str, default="master")
    parser.add_argument('--head', help='branch to merge', type=str, default=repo.head.shorthand)
    parser.add_argument('--issue', help='issue to reference', type=str, default='')
    parser.add_argument('-t', '--title', help='title', type=str, default='merge {}'.format(repo.head.shorthand))
    parser.add_argument('-m', '--message', help='message', type=str, default='merging {}'.format(repo.head.shorthand))
    subargs = parser.parse_args(args.tail)

    gh_pr = gh_repo.create_pull(
        title=subargs.title,
        body=subargs.message,
        base=subargs.into,
        head=subargs.head,
        maintainer_can_modify=True)
    assert gh_pr, "could not create pull request"
    print('created pull request:', gh_pr.html_url)


###----

def main(args):
    remo = repo.remotes[args.remote]
    url = giturlparse.parse(remo.url)

    tokens = []
    if args.token != '':
        tokens.append(args.token)
    tokens.extend(list(map(lambda t: t.value, filter(lambda h: h.name == 'hub.'+url.resource+'.token', repo.config.__iter__()))))
    url_http = 'https://{}/{}'.format(url.resource, url.pathname)
    url_api = 'https://{}/api/v3'.format(url.resource)

    gh = None
    for t in tokens:
        # Github Enterprise with custom hostname
        gh = Github(base_url=url_api, login_or_token=t)
        if gh:
            break
    assert gh, "could not access remote repo at {}".format(url_http)
    gh_repo = ghGetRepo(gh, url.owner, url.name)
    assert gh_repo, "could retrieve remote repo at {}".format(url_http)

    action = None
    action_name = re.sub(r'\W+', '', args.action)
    if hasattr(sys.modules[__name__], action_name):
        action = getattr(sys.modules[__name__], action_name)
    assert action, "{} is not a defined action".format(args.action)
    action(args, gh_repo)

###----

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', help='override user token', type=str, default="")
    parser.add_argument('remote', help='git remote to use', type=str)
    parser.add_argument('action', help='action to take on remote', type=str)
    parser.add_argument('tail', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    main(args)

###----
