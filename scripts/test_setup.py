import argparse
import contextlib
import json
import logging
import os
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

URL_BASE = 'https://github.com/{}.git'
parser = argparse.ArgumentParser()
parser.add_argument('env')
parser.add_argument('--tag', action='store_true')


def version_info():
    conda_list = subprocess.check_output(['conda', 'list', '--json'],
                                         universal_newlines=True)
    info_list = json.loads(conda_list)
    version_dict = {}

    for item in info_list:
        version_dict[item['name']] = item['version']

    return version_dict


def setup_all_tests(repo_file, tags=None):
    repo_file = Path(repo_file)

    with repo_file.open('r') as fd:
        repos = fd.read().strip().splitlines()

    for repo in repos:
        pkg = repo.split('/')[-1]
        if tags is None:
            setup_one_test(repo, pkg)
        else:
            try:
                tag = tags[pkg]
            except KeyError:
                logger.warning(
                    'Did not find package %s in environment, cannot use tag',
                    pkg,
                )
                setup_one_test(repo, pkg)
            else:
                setup_one_test(repo, pkg, tag=tag)


def setup_one_test(repo, pkg, tag=None):
    url = URL_BASE.format(repo)
    try:
        subprocess.run(['git', 'clone', url, '--depth', '1'],
                       check=True)
    except subprocess.CalledProcessError as err:
        raise RuntimeError(f'Error cloning from {url}') from err

    if tag is not None:
        print('Checking out package tag')
        with pushd(pkg):
            try:
                subprocess.run(
                    ['git', 'fetch', '--tags'],
                    check=True,
                )
                tag_prefix = subprocess.check_output(
                    ['git', 'tag', '-l'],
                    universal_newlines=True,
                ).strip().split('\n')[-1][0]
                if tag_prefix.isdigit():
                    tag_prefix = ''
                subprocess.run(
                    ['git', 'checkout', tag_prefix + tag],
                    check=True,
                )
            except subprocess.CalledProcessError as err:
                raise RuntimeError('Error checking out tag') from err
    # Set up submodules after tag to keep it synced to the tag
    with pushd(pkg):
        subprocess.run(['git', 'submodule', 'update', '--init', '--recursive'])


@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    yield
    os.chdir(previous_dir)


def main(args):
    print('Running pcds-envs test setup')

    pcds_envs = Path(__file__).resolve().parent.parent
    repo_file = pcds_envs / 'envs' / args.env / 'package-tests.txt'

    if args.tag:
        tags = version_info()

        if len(tags) == 0:
            print('No packages in current environment to test, quitting')
            return
    else:
        tags = None

    os.mkdir('tests')
    with pushd('tests'):
        setup_all_tests(repo_file, tags=tags)


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
