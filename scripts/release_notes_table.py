import collections
import dataclasses
import itertools
import pathlib
import re
import subprocess
import sys
import typing

import pkg_resources
import prettytable

# How much of a change is enough to include in the table?
VER_DEPTH = {
    'pcds': 3,
    'slac': 3,
    'lab': 3,
    'community': 2,
    'other': 1,
}

# Section headers
HEADERS = {
    'pcds': 'PCDS Package Updates',
    'slac': 'SLAC Package Updates',
    'lab': 'Lab Community Package Updates',
    'community': 'Python Community Core Package Updates',
    'other': 'Other Python Community Major Updates',
}

# List of packages to include in PCDS table
PCDS_PACKAGES = [
    'ads-async',
    'blark',
    'happi',
    'hutch-python',
    'hxrsnd',
    'lightpath',
    'lucid',
    'nabs',
    'pcdscalc',
    'pcdsdaq',
    'pcdsdevices',
    'pcdsutils',
    'pcdswidgets',
    'pmgr',
    'pswalker',
    'pyca',
    'pytmc',
    'tc_release',
    'transfocate',
    'typhos',
    'whatrecord',
]
# List of packages to include in SLAC table
SLAC_PACKAGES = [
    'elog',
    'psdaq-control-minimal',
    'psdm_qs_cli',
    'pydm',
    'timechart',
]
# List of packages to include in LAB table
LAB_PACKAGES = [
    'bluesky',
    'bluesky-live',
    'caproto',
    'databroker',
    'epicscorelibs',
    'ophyd',
    'pcaspy',
    'pyepics',
]
# List of packages to include in (notable) COMMUNITY table
COMMUNITY_PACKAGES = [
    'doctr',
    'flake8',
    'ipython',
    'jupyter',
    'numpy',
    'opencv',
    'pandas',
    'python',
    'pytest',
    'scikit-image',
    'scikit-learn',
    'scipy',
    'sphinx',
    'xarray',
]
# If missing from all above, belongs in OTHER table
# TODO if any of the above strings are not found in the env, error
PACKAGES = {
    'pcds': PCDS_PACKAGES,
    'slac': SLAC_PACKAGES,
    'lab': LAB_PACKAGES,
    'community': COMMUNITY_PACKAGES,
}

# For looking through a git diff
# First capture group is + or - (new version or old version)
# Second capture group is package name
# Third capture group is version string
ver_change_regex = re.compile(r'^(\+|\-)\s+\- ([^=\n]*)=+([^=\n]*)=?.*$', flags=re.M)

# For looking through the normal file
# Capture group is the package name
package_name_regex = re.compile(r'\s+\- ([^=\n]*)=+[^=\n]*=.*$', flags=re.M)


@dataclasses.dataclass
class Update:
    package_name: str
    old_version: typing.Optional[str] = None
    new_version: typing.Optional[str] = None

    def ver_depth(self) -> int:
        """
        Return a number indicating how big of an update it was.

        -1 = removed package
         0 = new package
         1 = Major release
         2 = Minor release
         3 = Bugfix
         4 or higher: non-semantic nonsense
        """
        if self.new_version is None:
            return -1
        if self.old_version is None:
            return 0
        old_parts = self.old_version.split('.')
        new_parts = self.new_version.split('.')
        for depth, (old, new) in enumerate(
            itertools.zip_longest(old_parts, new_parts, fillvalue='0')
        ):
            if old != new:
                return depth + 1
        raise RuntimeError(
            f'Could not interpret update for package "{self.package_name}" '
            f'from "{self.old_version}" to "{self.new_version}"'
        )

    def get_row(self) -> list[str]:
        return [self.package_name, self.old_version, self.new_version]

    def release_link(self) -> str:
        return (
            f'https://github.com/pcdshub/{self.package_name}'
            f'/releases/tag/v{self.new_version}'
        )

    @property
    def added(self) -> bool:
        return self.old_version is None and self.new_version is not None

    @property
    def removed(self) -> bool:
        return self.new_version is None and self.old_version is not None

    @property
    def updated(self) -> bool:
        return self.new_version != self.old_version


def get_package_updates(
    path: typing.Union[str, pathlib.Path],
    reference: str = 'master',
) -> dict[str, Update]:
    """Scans a git diff of the env.yaml file for changes."""
    diff_output = subprocess.check_output(
        ['git', 'diff', reference, str(path)],
        universal_newlines=True,
    )
    matches = ver_change_regex.findall(diff_output)
    updates = {}
    for diff_type, package_name, version_str in matches:
        try:
            entry = updates[package_name]
        except KeyError:
            entry = Update(package_name=package_name)
            updates[package_name] = entry
        if diff_type == '+':
            entry.new_version = version_str
        elif diff_type == '-':
            entry.old_version = version_str
        else:
            raise RuntimeError(
                f'Unexpected diff_type {diff_type} for {package_name}'
            )
    return updates


def build_tables(
    updates: dict[str, Update]
) -> dict[str, prettytable.PrettyTable]:
    """Makes the tables that we'd like to display in the update notes."""
    headers = ('Package', 'Old', 'New')
    table_names = ('pcds', 'slac', 'lab', 'community', 'other')
    tables = {name: prettytable.PrettyTable() for name in table_names}
    tables['pcds'].field_names = list(headers) + ['Release_Notes']
    for name in table_names[1:]:
        tables[name].field_names = headers
    for update in updates.values():
        if update.added or update.removed:
            continue
        row_added = False
        for group, package_list in PACKAGES.items():
            if update.package_name in package_list:
                if update.updated and update.ver_depth() <= VER_DEPTH[group]:
                    # Include this in the table
                    row = update.get_row()
                    if group == 'pcds':
                        row += [update.release_link()]
                    tables[group].add_row(row)
                    row_added = True
                    break
        if (
            update.updated
            and not row_added
            and update.ver_depth() <= VER_DEPTH['other']
        ):
            tables['other'].add_row(update.get_row())
    return tables


def audit_package_lists(path):
    """Find typos in the package list globals."""
    with open(path, 'r') as fd:
        lines = fd.read()

    packages = set(package_name_regex.findall(lines))
    err = []
    for package_list in PACKAGES.values():
        for package_name in package_list:
            if package_name not in packages:
                err.append(package_name)
    if err:
        raise RuntimeError(
            'Found package names that are not installed! '
            'Check your spelling and environment! '
            f'{err}'
        )


def build_reverse_deps_cache() -> dict[str, set]:
    """For each installed package, find the packages that require it."""
    reverse_deps_cache = collections.defaultdict(set)
    for pkg_name, dist in pkg_resources.working_set.by_key.items():
        variants = [pkg_name] + list(determine_installed_extras(pkg_name))
        for variant in variants:
            reqs = pkg_resources.require(variant)
            for req in reqs:
                reverse_deps_cache[req.key].add(pkg_name)
    return reverse_deps_cache


def determine_installed_extras(package: str) -> list[str]:
    """Figure out which extras variants of package are installed."""
    distribution = pkg_resources.get_distribution(package)
    all_extras = distribution.extras
    installed_extras = set()
    for extra in all_extras:
        try:
            variant = f'{package}[{extra}]'
            pkg_resources.require(variant)
        except (
            pkg_resources.DistributionNotFound,
            pkg_resources.ContextualVersionConflict,
        ):
            continue
        installed_extras.add(variant)
    return installed_extras


def main(env_name='pcds', reference='master'):
    path = f'../envs/{env_name}/env.yaml'
    audit_package_lists(path)
    updates = get_package_updates(path, reference)
    reverse_deps_cache = build_reverse_deps_cache()
    # First, added/removed packages
    added_pkgs = set()
    removed_pkgs = []
    for update in updates.values():
        if update.added:
            added_pkgs.add(update.package_name)
        elif update.removed:
            removed_pkgs.append(update.package_name)
    added_reqs = {pkg for pkg in added_pkgs if len(reverse_deps_cache[pkg]) > 1}
    added_specs = added_pkgs.difference(added_reqs)
    if added_specs:
        header = 'Added the Following Packages'
        print(header)
        print('-' * len(header))
        print()
        for pkg in sorted(added_specs):
            print(f'- {pkg}')
        print()
    if added_reqs:
        header = 'Added the Following Dependencies'
        print(header)
        print('-' * len(header))
        print()
        for pkg in sorted(added_reqs):
            print(f'- {pkg} (required by {", ".join(sorted(reverse_deps_cache[pkg]))})')
        print()
    if removed_pkgs:
        header = 'Removed the Following Packages'
        print(header)
        print('-' * len(header))
        print()
        for pkg in sorted(removed_pkgs):
            print(f'- {pkg}')
        print()
    # Next, updates by category
    tables = build_tables(updates)
    for name, table in tables.items():
        if len(list(table)) > 0:
            print(HEADERS[name])
            divider = '-' * len(HEADERS[name])
            print(divider)
            print()
            table.set_style(prettytable.MARKDOWN)
            print(table)
            print()


if __name__ == '__main__':
    main(*sys.argv[1:])
