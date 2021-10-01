import argparse
import json
import re
import requests
import subprocess
from pathlib import Path

from packaging import version


CHANNELS = ['conda-forge', 'pcds-tag', 'lcls-ii']

def latest_version(package):
    try:
        info = subprocess.check_output(['conda', 'search', '--json', package],
                                       universal_newlines=True)
    except Exception as exc:
        raise
    info_list = json.loads(info)[package]
    channel_versions = {}
    latest_version = "0.0.0"
    for info_item in info_list:
        item_version = info_item['version']
        item_channel = info_item['channel']
        for ch in CHANNELS:
            if ch in item_channel:
                item_channel = ch
                break
        if version.parse(item_version) > version.parse(latest_version):
            latest_version = item_version
        latest_ch_ver = channel_versions.setdefault(item_channel, "0.0.0")
        if version.parse(item_version) > version.parse(latest_ch_ver):
            channel_versions[item_channel] = item_version
    if channel_versions.get('conda-forge', latest_version) != latest_version:
        print(
            f'Warning! {package}={latest_version} '
            'is not ready on conda-forge! '
            'Building with this config is likely to fail!'
            )
    return latest_version


pypi_version_re = re.compile(f'-(\d\.\d\.\d).tar.gz')

def pypi_latest_version_no_search(package):
    req = requests.get(f'https://pypi.org/project/{package}')
    matches = set(pypi_version_re.findall(req.text))
    if not matches:
        raise RuntimeError(f'{package} not found on pypi.')
    latest_version = '0.0.0'
    for ver in matches:
        if version.parse(ver) > version.parse(latest_version):
            latest_version = ver
    return ver


def update_specs(path, versions_dict, dry_run=False):
    if not path.exists():
        print(f'{path} does not exist, skipping')
        return
    print(f'Updating {path} specs...')

    with path.open('r') as fd:
        specs = fd.readlines()

    changed_spec = False
    for i, spec in enumerate(specs):
        package = re.split('\=|>|<| |\n', spec)[0]
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
        print(f'Writing changes for package specs')
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
            packages = fd.readlines()
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
        package = package.strip('\n')
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
