#!/usr/bin/env python3.8
"""Tasks file used by the *invoke* command.

This simplifies some common development tasks.

Run these tasks with the `invoke` tool.
"""

from __future__ import annotations

import sys
import os
import shutil
import getpass
from glob import glob

import keyring
from invoke import task, run, Exit

SIGNERS = {"keithdart": "kdart"}

PYTHONBIN = os.environ.get("PYTHONBIN", sys.executable)
# Put the path in quotes in case there is a space in it.
PYTHONBIN = f'"{PYTHONBIN}"'

GPG = "gpg2"

CURRENT_USER = getpass.getuser()

# Package repo location. Putting info here eliminates the need for user-private ~/.pypirc file.
REPO_HOST = "pypi.org"
REPO_PORT = 80
REPOSITORY_URL = f"http://{REPO_HOST}:{REPO_PORT}/"
REPO_USERNAME = SIGNERS.get(CURRENT_USER)
REPO_INDEX = f"{REPOSITORY_URL}simple"


@task
def info(ctx):
    """Show information about the current Python and environment."""
    suffix = get_suffix()
    version = open("VERSION").read().strip()
    print(f"Project version: {version}")
    print(f"Python being used: {PYTHONBIN}")
    print(f"Python extension suffix: {suffix}")
    print(f"repo URL: {REPOSITORY_URL} User: {REPO_USERNAME}")


@task
def set_repo_password(ctx):
    """Set the password in the local key ring for the Artifactory account used as the package repo.
    """
    pw = getpass.getpass(f"Password for {REPO_USERNAME} account on {REPO_HOST}? ")
    if pw:
        repeat_pw = getpass.getpass("Please repeat it: ")
        if repeat_pw == pw:
            keyring.set_password(REPO_HOST, REPO_USERNAME, pw)
        else:
            raise Exit("Passwords did not match!", 2)
    else:
        raise Exit("No password entered.", 3)


@task
def build(ctx):
    """Build the intermediate package components."""
    ctx.run(f"{PYTHONBIN} setup.py build")


@task
def dev_requirements(ctx):
    """Install development requirements."""
    ctx.run(f"{PYTHONBIN} -m pip install --index-url {REPO_INDEX} --trusted-host {REPO_HOST} "
            f"-r requirements_dev.txt --user")


@task(pre=[dev_requirements])
def develop(ctx, uninstall=False):
    """Start developing in developer mode."""
    if uninstall:
        ctx.run(f"{PYTHONBIN} setup.py develop --uninstall --user")
    else:
        ctx.run(f'{PYTHONBIN} setup.py develop --index-url "{REPO_INDEX}" --user')


@task
def clean(ctx):
    """Clean out build and cache files. Remove extension modules."""
    ctx.run(f"{PYTHONBIN} setup.py clean")
    ctx.run(r"find . -depth -type d -name __pycache__ -exec rm -rf {} \;")
    ctx.run('find ssh2 -name "*.so" -delete')
    with ctx.cd("doc"):
        ctx.run(f"{PYTHONBIN} -m sphinx.cmd.build -M clean . _build")


@task
def cleandist(ctx):
    """Clean out dist subdirectory."""
    if os.path.isdir("dist"):
        shutil.rmtree("dist", ignore_errors=True)
        os.mkdir("dist")


@task
def test(ctx, testfile=None, ls=False):
    """Run unit tests. Use ls option to only list them."""
    if ls:
        ctx.run(f"{PYTHONBIN} -m pytest --collect-only -qq tests")
    elif testfile:
        ctx.run(f"{PYTHONBIN} -m pytest -s {testfile}")
    else:
        ctx.run(f"{PYTHONBIN} -m pytest tests", hide=False, in_stream=False)


@task(cleandist)
def sdist(ctx):
    """Build source distribution."""
    ctx.run(f"{PYTHONBIN} setup.py sdist")


@task
def build_ext(ctx):
    """Build compiled extension modules, in place."""
    ctx.run(f"{PYTHONBIN} setup.py build_ext --inplace")


@task(sdist)
def bdist(ctx):
    """Build a standard wheel file, an installable format."""
    ctx.run(f"{PYTHONBIN} setup.py bdist_wheel")


@task(bdist)
def sign(ctx):
    """Cryptographically sign dist with your default GPG key."""
    if CURRENT_USER in SIGNERS:
        ctx.run(f"{GPG} --detach-sign -a dist/ssh2-*.whl")
        ctx.run(f"{GPG} --detach-sign -a dist/ssh2-*.tar.gz")
    else:
        print("Not signing.")


@task(pre=[sign])
def publish(ctx):
    """Publish built wheel file to internal package repo."""
    pw = get_repo_password()
    distfiles = glob("dist/*.whl")
    distfiles.extend(glob("dist/*.tar.gz"))
    if not distfiles:
        raise Exit("Nothing in dist folder!")
    distfiles = " ".join(distfiles)
    ctx.run(f'{PYTHONBIN} -m twine upload --repository-url \"{REPOSITORY_URL}\" '
            f'--username {REPO_USERNAME} --password {pw} {distfiles}')


@task
def docs(ctx):
    """Build the HTML documentation."""
    with ctx.cd("doc"):
        ctx.run(f"{PYTHONBIN} -m sphinx.cmd.build -M html . _build")
    if os.environ.get("DISPLAY"):
        ctx.run("xdg-open docs/_build/html/index.html")


@task
def branch(ctx, name=None):
    """start a new branch, both local and remote tracking."""
    if name:
        ctx.run(f"git checkout -b {name}")
        ctx.run(f"git push -u origin {name}")
    else:
        ctx.run("git --no-pager branch")


@task
def branch_delete(ctx, name=None):
    """Delete local, remote and tracking branch by name."""
    if name:
        ctx.run(f"git branch -d {name}", warn=True)  # delete local branch
        ctx.run(f"git branch -d -r {name}", warn=True)  # delete local tracking info
        ctx.run(f"git push origin --delete {name}", warn=True)  # delete remote (origin) branch.
    else:
        print("Supply a branch name: --name <name>")


def get_repo_password():
    cred = keyring.get_credential(REPO_HOST, REPO_USERNAME)
    if not cred:
        raise Exit("You must set the Artifactory password first with set-password target.", 1)
    return cred.password


def get_suffix():
    return run(
        f'{PYTHONBIN} -c \'import sysconfig; print(sysconfig.get_config_vars()["EXT_SUFFIX"])\'',
        hide=True,
    ).stdout.strip()  # noqa
