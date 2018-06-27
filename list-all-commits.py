#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function

import os
import sys

from sh import git

from github import github

def logit(*args):
    print(*args, file=sys.stderr)

if len(sys.argv) >= 2:
    org = sys.argv[1]
    destpath = len(sys.argv) > 2 and sys.argv[2] or "./repos"
    later = len(sys.argv) > 3 and sys.argv[3] or ""
    skip_to = len(sys.argv) > 4 and sys.argv[4] or None
    reached = False
    
    d = os.getcwd()
    repos = github("repos", org, project=None)
    logit("Repos:\n", "\t" + "\n\t".join([r.get("pushed_at") + " " + r.get("name") for r in repos]))
    for r in repos:
        repo = r.get("name")
        if not skip_to or repo == skip_to:
            reached = True
        if not r.get("archived") and r.get("pushed_at") > later and reached:
            logit("Checking %s" % repo)
            repopath = os.path.join(destpath, repo)
            if not os.path.exists(repopath):
                logit("Cloning", repo, "into", repopath)
                git("clone", "git@github.com:" + org + "/" + repo + ".git", repopath)
            os.chdir(repopath)
            
            remotes = git("remote").split("\n")
            logit("Retrieving forks for", repo)
            forks = github("forks", org, project=repo)
            logit("Forks:", " ".join([f.get("owner").get("login") for f in forks]))
            for f in forks:
                login = f.get("owner").get("login")
                if not login in remotes:
                    #print login, f.get("pushed_at"), f.get("updated_at")
                    logit("Adding remote", login, "to", repo)
                    git("remote", "add", login, "git@github.com:" + login + "/" + repo + ".git")
                logit("Fetch fork:", login)
                git("fetch", login)
            for r in ["master", "dev", "live"]:
                if r in remotes:
                    logit("Fetch branch:", r)
                    git("fetch", r)
            
            logit("Generating log", repo)
            try:
                git("log", "--remotes", "--all", "--date=short", "--date-order", "--pretty=tformat:" + repo + "%x09%cd%x09%an%x09%h%x09%s", _out=sys.stdout)
            except Exception, e:
                logit("Git exception:", str(e))
            os.chdir(d)
        else:
            logit("Skipping repo:", repo, r.get("pushed_at"))
else:
    logit("Usage: " + sys.argv[0] + " ORGANISATION [REPOSITORIES-DOWNLOAD-PATH] [UPDATED-AFTER-DATE] [SKIP-TO-REPOSITORY]")
    logit("REPOSITORIES-DOWNLOAD-PATH defaults to ./repos")
    logit("UPDATED-AFTER-DATE will only fetch projects which ahve been pushed to after date. Format: 2018-06-01T00:00:00Z")
    logit("SKIP-TO-REPOSITORY is useful if the process is interrupted half way though.")

