"""
Script for accumulating the optional extras of an as-installed environment.

There is currently no way in conda to install the "test" requirements from a
recipe into the env.

We could parse the recipes ourselves, but then we're still missing the docs
requirements.

Once a package is installed, the "test" and "doc" extras will be present in the
metadata even if we haven't installed them yet, and then we can inspect them
with the importlib.metadata module.
"""
from __future__ import annotations

import logging
from argparse import ArgumentParser
from collections.abc import Iterator
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path

logger = logging.getLogger(__name__)


# Packages that are only available on Conda
CONDA_ONLY = []
# Packages that are only available on PYPI
PYPI_ONLY = []
# Packages that can't be put into the environment right now
AVOID = ['python-ldap']


@dataclass(frozen=True)
class PackageSpec:
    # Just the install name e.g. pcdsdevices
    name: str
    # Install name with pypi extra e.g. pcdsdevices[doc]
    name_with_extra: str
    # Any pinning information e.g. >=7.0.1
    pin: str | None
    # Just the extra of this spec e.g. doc
    spec_extra: str | None
    # The extra classification of the package that requires this one
    source_extra: str | None

    @classmethod
    def from_importlib_metadata(cls, spec: str) -> PackageSpec:
        """
        Parse an importlib metadata spec.

        These specs look something like:
        "sphinx (<7.0.0) ; extra = 'doc'"
        But if the package is not pinned or it is not an extra it may just be:
        "sphinx"
        And sometimes there can be further specifiers like:
        "mkdocstrings[python]"
        which all need to be handled appropriately.

        Parameters
        ----------
        spec : str
            A spec string from importlib.metadata.Distribution.requires, which
            should always be a list of such strings.
        """
        name_with_extra = spec.split(" ")[0]
        if "[" in name_with_extra:
            name, spec_extra = name_with_extra.split("[")
            spec_extra = spec_extra.strip("]")
        else:
            name = name_with_extra
            spec_extra = None
        if "(" in spec:
            pin = spec.split("(")[1].split(")")[0]
        else:
            pin = None
        if "; extra" in spec:
            source_extra = spec.split("; extra == ")[1].strip("'")
        else:
            source_extra = None
        return cls(
            name=name,
            name_with_extra=name_with_extra,
            pin=pin,
            spec_extra=spec_extra,
            source_extra=source_extra,
        )

    def is_installed(self) -> bool:
        """
        Return True if this package is installed and False otherwise.
        """
        try:
            distribution(self.name)
            return True
        except PackageNotFoundError:
            return False


def get_packages(base: str) -> Iterator[str]:
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
    packages : iterator of str
        The package names that we want to use here.
    """
    extras_path = Path(__file__).parent.parent / "envs" / base / "install-extras.txt"
    with extras_path.open("r") as fd:
        return (yield from (line for line in fd.read().splitlines() if line))


def get_package_extra_deps(package: str) -> Iterator[PackageSpec]:
    """
    Given a package name, get all of the dependencies of just the extras.

    This does not include the core dependencies of the package and does not
    include any pinning information.
    Note that these dependencies use the pypi names, not the conda names, in case
    of a conflict.

    Parameters
    ----------
    package : str
        The name of the package to check

    Returns
    -------
    dependencies : iterator of PackageSpec
        All dependencies of the package extras. Uses the pypi names.
    """
    try:
        full_reqs = distribution(package).requires
    except PackageNotFoundError:
        logger.warning("%s is not installed and cannot be checked.", package)
        return set()
    specs = (PackageSpec.from_importlib_metadata(req) for req in full_reqs)
    return (yield from (pkg for pkg in specs if pkg.source_extra))


def get_env_extra_deps(base: str) -> set[PackageSpec]:
    """
    Given a base environment, get all of the extras to include.

    Converts to a set to remove duplicates.

    Parameters
    ----------
    base : str
        The environment name, e.g. pcds.

    Returns
    -------
    dependencies : set of PackageSpec
        All pypi depenencies of the package extras.
    """
    deps = set()
    for package_name in get_packages(base=base):
        deps.update(get_package_extra_deps(package=package_name))
    return deps


def get_missing_dependencies(all_deps: Iterator[PackageSpec]) -> Iterator[PackageSpec]:
    """
    Return a reduced set of dependencies: only the ones that are not installed

    Parameters
    ----------
    all_deps : set of str
        All dependencies to consider.

    Returns
    -------
    missing_deps : set of PackageSpec
        A new set that only includes the dependencies that are not installed.
    """
    return (yield from (dep for dep in all_deps if not dep.is_installed()))


def main(base: str, for_pypi: bool) -> int:
    """
    Get all missing extras dependencies in the current env and send them to stdout.

    Parameters
    ----------
    base : str
        The environment name, e.g. pcds.

    for_pypi : bool
        Whether or not to include the pypi extras string
    """
    all_deps = get_env_extra_deps(base=base)
    missing_deps = get_missing_dependencies(all_deps=all_deps)
    if for_pypi:
        pkg_to_print = set(dep.name_with_extra for dep in missing_deps if dep.name not in CONDA_ONLY + AVOID)
    else:
        pkg_to_print = set(dep.name for dep in missing_deps if dep.name not in PYPI_ONLY + AVOID)
    print("\n".join(sorted(list(pkg_to_print))))
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
        help="Enable verbose error messages",
    )
    parser.add_argument(
        "--for-pypi",
        action="store_true",
        help=(
            "Produce the file specs you should use for pypi instead of "
            "those to be used for conda. Different packages may be included "
            "depending on if this flag is included or not. This flag also "
            "includes the extras spec e.g. pcdsdevices[doc] instead of just "
            "pcdsdevices. You likely want this when installing "
            "from pypi but not when installing from conda."
        )
    )
    args = parser.parse_args()
    try:
        exit(main(base=args.base, for_pypi=args.for_pypi))
    except Exception as exc:
        if args.verbose:
            raise
        print(exc)
        exit(1)
