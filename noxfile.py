#!/usr/bin/python3

import nox

_python_app_dir = "src"
_requirements_app = f"{_python_app_dir}/requirements/requirements.txt"
_requirements_tests = f"{_python_app_dir}/requirements/requirements_pytests.txt"


@nox.session
def format(session):
    session.install("-r", _requirements_tests)
    session.run("black", ".")


@nox.session()
def lint(session):
    session.install("-r", _requirements_tests)
    session.install("-r", _requirements_app)
    session.run("python", "--version")
    session.run("flake8", "--max-line-length=120", "--exclude=venv,__pycache__,.nox")
    session.run("pylint", f"{_python_app_dir}", "--extension-pkg-allow-list=")


@nox.session(python=["3.12", "3.10"])
def test(session):
    session.install("-r", _requirements_tests)
    session.install("-r", _requirements_app)
    session.run("pytest", *session.posargs)
