import argparse
import json
import re
import subprocess
from packaging import version
from pathlib import Path


def latest_version(package):
    info = subprocess.check_output(['conda', 'search', '--json', package],
                                   universal_newlines=True)
    info_list = json.loads(info)[package]
    latest_version = "0.0.0"
    for info_item in info_list:
        item_version = info_item['version']
        if version.parse(item_version) > version.parse(latest_version):
            latest_version = item_version
    return latest_version


def update_specs(path, versions_dict, dry_run=False):
    if not path.exists():
        print(f'{path} does not exist, skipping')
        return
    print(f'Updating {path} specs...')

    with path.open('r') as fd:
        specs = fd.readlines()

    changed_spec = []
    for i, spec in enumerate(specs):
        package = re.split(spec, '\=|>|<| ')[0]
        try:
            latest = versions_dict[package]
            specs[i] = f'{package}>={latest}'
            changed_spec.append(package)
        except KeyError:
            pass

    if changed_spec:
        print(f'Writing changes for packages {changed_spec}')
        if dry_run:
            print('Skip write because this is a dry run')
        else:
            with path.open('w') as fd:
                fd.writelines(specs)
    else:
        print('No changes found')


def main(args):
    env = args.env

    here = Path(__file__).parent
    env_folder = here / '../envs/' / env

    conda_packages = env_folder / 'conda-packages.txt'
    pip_packages = env_folder / 'pip-packages.txt'
    keep_updated = env_folder / 'keep-updated.txt'

    packages = []
    if keep_updated.exists():
        with keep_updated.open('r') as fd:
            packages = fd.readlines()
    if not packages:
        return

    versions_dict = {}
    for package in packages:
        package = package.strip('\n')
        latest = latest_version(package)
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

    main(parser.parse_args())
