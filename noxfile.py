"""Declaration of Nox commands which can be run for this package"""

import hashlib
from collections.abc import Iterable
from pathlib import Path

import nox
import nox.virtualenv

PYTHON_VERSIONS = ["3.11", "3.12"]
PACKAGE_NAME = "spotfishing"


def install_groups(
    session: nox.Session,
    *,
    include: Iterable[str] = (),
    include_self: bool = True,
) -> None:
    """Install Poetry dependency groups.

    Install the given dependency groups into the session's virtual environment.
    When 'include_self' is true, also installs this package and default dependencies.

    We cannot use `poetry install` here, because it ignores the
    session's environment and installs into Poetry's own environment.
    Instead, use `poetry export` with suitable options to generate a requirements.txt
    file to pass to session.install().

    Auto-skip the `poetry export` step if neither the poetry.lock file nor the export
    command has changed (matching hash) since the last time this session was run.
    """
    if isinstance(session.virtualenv, nox.virtualenv.PassthroughEnv):
        session.warn(
            "Running outside a Nox virtualenv! We will skip installation here, "
            "and simply assume that the necessary dependency groups have "
            "already been installed by other means!"
        )
        return

    lockdata = Path("poetry.lock").read_bytes()
    requirements_txt = Path(session.cache_dir, session.name, "reqs_from_poetry.txt")
    argv = [
        "poetry",
        "export",
        "--format=requirements.txt",
        # pip checks hashes for all requirements or none, and gertils, a git dependency, has
        # none. So pip checks none here; CI and the Nix shell install with Poetry, which does.
        "--without-hashes",
        f"--output={requirements_txt}",
    ]
    if include:
        option = "only" if not include_self else "with"
        argv.append(f"--{option}={','.join(include)}")
    # The export depends on the lock file and on the command, so a change to either renews it.
    digest = hashlib.blake2b(lockdata + " ".join(argv).encode()).hexdigest()
    hashfile = requirements_txt.with_suffix(".hash")

    if not hashfile.is_file() or hashfile.read_text() != digest:
        session.log(f"Will generate requirements hashfile: {hashfile}")
        requirements_txt.parent.mkdir(parents=True, exist_ok=True)
        session.debug(f"Running command: {' '.join(argv)}")
        session.run_always(*argv, external=True)
        session.debug(f"Writing requirements hashfile: {hashfile}")
        hashfile.write_text(digest)

    session.log("Installing requirements")
    session.install("-r", str(requirements_txt))
    if include_self:
        session.log(f"Installing {PACKAGE_NAME}")
        session.install("-e", ".")
    else:
        session.debug(f"Skipping installation of {PACKAGE_NAME}")


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the tests."""
    install_groups(session, include=["test"])
    session.run(
        "pytest",
        "-x",
        "--cov",
        "--log-level=debug",
        "--durations=10",
        "--hypothesis-show-statistics",
        *session.posargs,
    )


@nox.session(python=PYTHON_VERSIONS)
def lint(session: nox.Session) -> None:
    """Check the types with pyright and lint with ruff."""
    install_groups(session, include=["lint"])
    session.run("pyright")
    session.run("ruff", "check")


@nox.session(name="format")
def check_format(session: nox.Session) -> None:
    """Check the spelling, the order of the imports and the layout."""
    install_groups(session, include=["format"], include_self=False)
    session.run("codespell", "--enable-colors")
    session.run("ruff", "check", "--select=I", "--diff")
    session.run("ruff", "format", "--check", "--diff")


@nox.session
def reformat(session: nox.Session) -> None:
    """Fix the spelling, the order of the imports and the layout."""
    install_groups(session, include=["format"], include_self=False)
    session.run("codespell", "--write-changes")
    session.run("ruff", "check", "--select=I", "--fix")
    session.run("ruff", "format")
