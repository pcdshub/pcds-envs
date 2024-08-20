import argparse
import re
import subprocess
from pathlib import Path

import requests
from binstar_client import Binstar
from binstar_client.errors import BinstarError
from packaging import version

CHANNELS = ['conda-forge', 'pcds-tag', 'lcls-ii']
client = None


def get_client() -> Binstar:
    global client
    if client is None:
        client = Binstar()
    return client


def latest_version(package):
    client = get_client()
    versions_list = None
    for ch in CHANNELS:
        try:
            info = client.package(ch, package)
        except BinstarError:
            continue
        else:
            # latest_version key is not necessarily correct, we need to check ourselves
            versions_list = info["versions"]
            break
    if versions_list is None:
        raise RuntimeError(f"{package} not found in any channel: {CHANNELS}")
    latest_version = "0.0.0"
    for item_version in versions_list:
        try:
            if version.parse(item_version) > version.parse(latest_version):
                latest_version = item_version
        except version.InvalidVersion:
            # Some packages can have malformed version numbers
            # Just ignore these and move on
            pass
    return latest_version


pypi_version_re = re.compile(r'-(\d\.\d\.\d).tar.gz')


def pypi_latest_version_no_search(package):
    req = requests.get(f'https://pypi.org/project/{package}')
    matches = set(pypi_version_re.findall(req.text))
    if not matches:
        raise RuntimeError(f'{package} not found on pypi.')
    latest_version = '0.0.0'
    for ver in matches:
        try:
            if version.parse(ver) > version.parse(latest_version):
                latest_version = ver
        except version.InvalidVersion:
            # Some packages can have malformed version numbers
            # Just ignore these and move on
            pass
    return latest_version


def update_specs(path, versions_dict, dry_run=False):
    if not path.exists():
        print(f'{path} does not exist, skipping')
        return
    print(f'Updating {path} specs...')

    with path.open('r') as fd:
        specs = fd.readlines()

    changed_spec = False
    for i, spec in enumerate(specs):
        package = re.split(r'\=|>|<| |\n', spec)[0]
        try:
            latest = versions_dict[package]
            spec = spec.strip('\n')
            new_spec = f'{package}>={latest}'
            if new_spec == spec:
                print(f'Will keep existing {package} spec {spec}')
            else:
                print(f'Will change {package} spec from {spec} to {new_spec}')
                specs[i] = new_spec + '\n'
                changed_spec = True
        except KeyError:
            pass

    if changed_spec:
        print('Writing changes for package specs')
        if dry_run:
            print('Skip write because this is a dry run')
        else:
            with path.open('w') as fd:
                fd.writelines(specs)
    else:
        print('No changes found')


def main(args):
    env = args.env

    here = Path(__file__).resolve().parent
    env_folder = here.parent / 'envs' / env

    conda_packages = env_folder / 'conda-packages.txt'
    pip_packages = env_folder / 'pip-packages.txt'
    keep_updated = env_folder / 'keep-updated.txt'

    packages = []
    if keep_updated.exists():
        with keep_updated.open('r') as fd:
            packages = [
                line.strip() for line in fd.readlines()
                if line.strip() and not line.startswith('#')
            ]
    else:
        print(f'{keep_updated} does not exist')
    if not packages:
        print(f'Found no packages in {keep_updated}, nothing to do')
        return

    if args.debug:
        conda_info = subprocess.check_output(['conda', 'info', '-a'],
                                             universal_newlines=True)
        print(conda_info)

    versions_dict = {}
    for package in packages:
        try:
            latest = latest_version(package)
        except Exception:
            latest = pypi_latest_version_no_search(package)
        versions_dict[package] = latest
        print(f'Latest version of {package} is {latest}')

    print('Updating specs. Make sure to verify and commit')
    update_specs(conda_packages, versions_dict, dry_run=args.dryrun)
    update_specs(pip_packages, versions_dict, dry_run=args.dryrun)
    print('Done')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('env')
    parser.add_argument('--dryrun', action='store_true')
    parser.add_argument('--debug', action='store_true')

    main(parser.parse_args())
