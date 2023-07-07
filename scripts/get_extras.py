"""
Script for accumulating the optional extras of an as-installed environment.

There is currently no way in conda to install the "test" requirements from a
recipe into the env.

We could parse the recipes ourselves, but then we're still missing the docs
requirements.

Once a package is installed, the "test" and "doc" extras will be present in the
metadata even if we haven't installed them yet, and then we can inspect them
with the pkg_resources module.
"""
import logging
from argparse import ArgumentParser
from pathlib import Path

from pkg_resources import DistributionNotFound, get_distribution

logger = logging.getLogger(__name__)


def get_packages(base: str) -> list[str]:
    """
    Given a base environment, get the packages to use here.

    We can't use every installed package and we don't want to write out the
    specifics here.

    Instead, we create a special file that defines which packages we want
    to install the extras for.

    Parameters
    ----------
    base : str
        The environment name, e.g. pcds.

    Returns
    -------
    packages : list of str
        The package names that we want to use here.
    """
    extras_path = Path(__file__).parent.parent / "envs" / base / "install-extras.txt"
    with extras_path.open("r") as fd:
        return [line for line in fd.read().splitlines() if line]


def get_all_extra_deps(package: str) -> set[str]:
    """
    Given a package name, get all of the dependencies of just the extras.

    This does not include the core dependencies of the package.
    Note that these dependencies use the pypi names, not the conda names, in case
    of a conflict.

    Parameters
    ----------
    package : str
        The name of the package to check

    Returns
    -------
    dependencies : set of str
        All pypi dependencies of the package extras.
    """
    try:
        dist = get_distribution(package)
    except DistributionNotFound:
        logger.warning("%s is not installed and cannot be checked.", package)
        return set()
    core_reqs = set(req.name for req in dist.requires())
    all_reqs = set(req.name for req in dist.requires(extras=dist.extras))
    return all_reqs - core_reqs


def get_env_extras(base: str) -> set[str]:
    """
    Given a base environment, get all of the extras to include.

    Parameters
    ----------
    base : str
        The environment name, e.g. pcds.

    Returns
    -------
    dependencies : list of str
        All pypi depenencies of the package extras.
    """
    deps = set()
    for package_name in get_packages(base=base):
        deps.update(get_all_extra_deps(package=package_name))
    return deps


def main(base: str) -> None:
    """
    Get all extras dependencies in the current env and send them to stdout.

    Parameters
    ----------
    base : str
        The environment name, e.g. pcds.
    """
    deps = sorted(list(get_env_extras(base=base)))
    print("\n".join(deps))
    return 0


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "base",
        type=str,
        help="Environment basename",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable erbose error messages",
    )
    args = parser.parse_args()
    try:
        exit(main(base=args.base))
    except Exception as exc:
        if args.verbose:
            raise
        print(exc)
        exit(1)
