import collections
import copy
import dataclasses
import itertools
import json
import pathlib
import re
import subprocess
import sys
import typing
import warnings

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
    'degraded': 'Packages With Degraded Versions',
}

# List of packages to include in PCDS table
PCDS_PACKAGES = [
    'ads-async',
    'atef',
    'blark',
    'elog',
    'happi',
    'hutch-python',
    'hxrsnd',
    'krtc',
    'lightpath',
    'lucid',
    'nabs',
    'pcdscalc',
    'pcdsdaq',
    'pcdsdevices',
    'pcdsutils',
    'pcdswidgets',
    'pmpsdb_client',
    'pmpsui',
    'pmgr',
    'psdaq-control-minimal',
    'pswalker',
    'pyca',
    'pytmc',
    'tc-release',
    'transfocate',
    'typhos',
    'whatrecord',
]
# List of packages to include in SLAC table
SLAC_PACKAGES = [
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
    'hklpy',
    'ophyd',
    'pcaspy',
    'pyepics',
    'suitcase-csv',
    'suitcase-json-metadata',
    'suitcase-jsonl',
    'suitcase-specfile',
    'suitcase-tiff',
]
# List of packages to include in (notable) COMMUNITY table
COMMUNITY_PACKAGES = [
    'flake8',
    'ipython',
    'jupyter',
    'numpy',
    'opencv',
    'pandas',
    'pre-commit',
    'pyqt',
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
ver_change_regex = re.compile(
    r'^(\+|\-)\s+\- ([^=\n]*)=+([^=\n]*)=?.*$',
    flags=re.M,
)

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

    def release_link(self, org='pcdshub') -> str:
        return (
            f'https://github.com/{org}/{self.package_name}'
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

    @property
    def degraded(self) -> bool:
        if self.new_version == self.old_version:
            return False
        try:
            new = pkg_resources.parse_version(self.new_version)
            old = pkg_resources.parse_version(self.old_version)
        except ValueError:
            # Invalid version, we can't tell!
            # Err on the side of false positives.
            return True
        return new < old


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
    table_names = ('pcds', 'slac', 'lab', 'community', 'other', 'degraded')
    tables = {name: prettytable.PrettyTable() for name in table_names}
    tables['pcds'].field_names = list(headers) + ['Release Notes']
    tables['slac'].field_names = list(headers) + ['Release Notes']
    for name in table_names[2:]:
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
                        row += [update.release_link('pcdshub')]
                    elif group == 'slac':
                        row += [update.release_link('slaclab')]
                    tables[group].add_row(row)
                    row_added = True
                    break
        if (
            update.updated
            and not row_added
            and update.ver_depth() <= VER_DEPTH['other']
        ):
            tables['other'].add_row(update.get_row())
        if update.degraded:
            tables['degraded'].add_row(update.get_row())
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


def build_reverse_deps_cache(
    subset: typing.Optional[typing.Iterable[str]] = None
) -> dict[str, set]:
    """
    For each installed package, find the packages that require it.

    Some packages are pypi-only, some packages are conda-only, and some
    share their dependencies with both.

    This finds all the python packages with well-formed dependencies, as this
    is discoverable in any given python environment, then extends the info
    using the "subset" argument if provided, or with the info discovered
    from mamba list. Afterwards, mamba repoquery seems to be the fastest
    way to build the dependency tree.
    """
    reverse_deps_cache = collections.defaultdict(set)
    # Use the standard python info
    for pkg_name, dist in pkg_resources.working_set.by_key.items():
        print(f'checking pkg_resources for {pkg_name}')
        extras = [None] + list(determine_installed_extras(pkg_name))
        distribution = pkg_resources.get_distribution(pkg_name)
        for extra in extras:
            if extra is None:
                reqs = distribution.requires()
            else:
                reqs = distribution.requires([extra])
            for req in reqs:
                if req.key != pkg_name:
                    reverse_deps_cache[req.key].add(pkg_name)
    # Use the mamba info to augment the above
    if subset is None:
        for pkg_name in mamba_list():
            print(f'checking mamba for {pkg_name}')
            dependencies = mamba_repoquery('depends', pkg_name)
            for dep in dependencies:
                if dep != pkg_name:
                    reverse_deps_cache[dep].add(pkg_name)
    else:
        for pkg_name in subset:
            print(f'checking mamba for {pkg_name}')
            needs = mamba_repoquery('whoneeds', pkg_name)
            reverse_deps_cache[pkg_name].update(
                [nd for nd in needs if nd != pkg_name]
            )
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
        installed_extras.add(extra)
    return installed_extras


def mamba_repoquery(command: str, package: str) -> list[str]:
    response = json.loads(
        subprocess.check_output([
            'mamba',
            'repoquery',
            command,
            '--offline',
            '--json',
            package,
        ])
    )
    return [spec['name'] for spec in response['result']['pkgs']]


def mamba_list() -> list[str]:
    response = json.loads(
        subprocess.check_output([
            'mamba',
            'list',
            '--json',
        ])
    )
    return [spec['name'] for spec in response]


def main(env_name='pcds', reference='master'):
    warnings.simplefilter('ignore')
    path = f'../envs/{env_name}/env.yaml'
    audit_package_lists(path)
    updates = get_package_updates(path, reference)

    # Prep work to build the dependency chain
    added_pkgs = set()
    removed_pkgs = []
    for update in updates.values():
        if update.added:
            added_pkgs.add(update.package_name)
        elif update.removed:
            removed_pkgs.append(update.package_name)
    reverse_deps_cache = build_reverse_deps_cache(added_pkgs)

    showed_update = False
    # First, show updates by category
    tables = build_tables(updates)
    for name, table in tables.items():
        if len(list(table)) > 0:
            showed_update = True
            print(HEADERS[name])
            divider = '-' * len(HEADERS[name])
            print(divider)
            print()
            table.set_style(prettytable.MARKDOWN)
            print(table)
            print()

    # Then, show added/removed packages
    # Split based on what pkg_resources knows about dependencies
    added_reqs = {
        pkg for pkg in added_pkgs if len(reverse_deps_cache[pkg]) > 0
    }
    added_specs = added_pkgs.difference(added_reqs)
    # Further refine the split based on mamba's knowledge
    if added_specs:
        showed_update = True
        header = 'Added the Following Packages'
        print(header)
        print('-' * len(header))
        print()
        for pkg in sorted(added_specs):
            print(f'- {pkg}')
        print()
    if added_reqs:
        showed_update = True
        header = 'Added the Following Dependencies'
        print(header)
        print('-' * len(header))
        print()
        core_packages = []
        for package_list in PACKAGES.values():
            core_packages.extend(package_list)
        for pkg in sorted(added_reqs):
            if pkg in core_packages:
                print(f'- {pkg} (new core package)')
            else:
                first_required = sorted(reverse_deps_cache[pkg])
                first_required_text = ', '.join(first_required)
                core_required = set()
                unresolved_chains = [[pkg]]
                while unresolved_chains:
                    for chain in copy.copy(unresolved_chains):
                        unresolved_chains.remove(chain)
                        deps = sorted(reverse_deps_cache.get(chain[0], []))
                        if not deps:
                            continue
                        for dep in deps:
                            if dep in chain:
                                continue
                            new_chain = [dep] + chain
                            if dep in core_packages:
                                # Include the core requires
                                core_required.add(dep)
                            else:
                                unresolved_chains.append(new_chain)
                for req in first_required:
                    try:
                        core_required.remove(req)
                    except KeyError:
                        pass
                if core_required:
                    if len(first_required) > 1:
                        are = 'are'
                    else:
                        are = 'is'
                    print(
                        f'- {pkg} (required by {first_required_text}, which '
                        f'{are} used in {", ".join(sorted(core_required))})'
                    )
                else:
                    print(f'- {pkg} (required by {first_required_text})')
        print()
    if removed_pkgs:
        showed_update = True
        header = 'Removed the Following Packages'
        print(header)
        print('-' * len(header))
        print()
        for pkg in sorted(removed_pkgs):
            print(f'- {pkg}')
        print()
    if not showed_update:
        print('No package updates.')


if __name__ == '__main__':
    main(*sys.argv[1:])
