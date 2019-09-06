import argparse
import configparser
import contextlib
import os
import requests
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--tag', action='store_true')


def version_info(channels):
    conda_list = subprocess.check_output(['conda', 'list'],
                                         universal_newlines=True)
    info = {}
    for line in conda_list.split('\n'):
        if any(ch in line for ch in channels):
            pkg, ver, _, _ = line.split()
            info[pkg] = ver
    return info


@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    yield
    os.chdir(previous_dir)


if __name__ == '__main__':
    print('Running pcds-envs test setup')
    args = parser.parse_args()

    info = version_info(['pcds-tag', 'pcds-dev'])
    github_orgs = ['pcdshub', 'slaclab']
    url_base = 'https://github.com/{org}/{pkg}'

    if len(info) == 0:
        print('No packages in current environment to test, quitting')

    for pkg, ver in info.items():
        print('Checking for tests on package {}...'.format(pkg))
        for org in github_orgs:
            # Check if url exists
            url = url_base.format(org=org, pkg=pkg)
            resp = requests.head(url)
            if resp.status_code >= 400:
                print('Skip {}/{}, nothing found'.format(org, pkg))
                url = None
            else:
                print('Setting up test for {}/{}'.format(org, pkg))
                break
        if url is None:
            continue
        subprocess.run(['git', 'clone', url])

        if args.tag:
            print('Checking out package tag')
            with pushd(pkg):
                config = configparser.ConfigParser()
                config.read('setup.cfg')
                tag_prefix = config['versioneer']['tag_prefix']
                subprocess.run(['git', 'checkout', tag_prefix + ver])
