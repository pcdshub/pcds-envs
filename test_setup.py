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
    args = parser.parse_args()

    info = version_info(['pcds-tag', 'pcds-dev'])

    for pkg, ver in info.items():
        # Check if url exists
        url = 'https://github.com/pcdshub/{}'.format(pkg)
        resp = requests.head(url)
        if resp.status_code >= 400:
            print('Skip {}, no repo on pcdshub'.format(pkg))
            continue
        subprocess.run(['git', 'clone', url])

        if args.tag:
            with pushd(pkg):
                config = configparser.ConfigParser()
                config.read('setup.cfg')
                tag_prefix = config['versioneer']['tag_prefix']
                subprocess.run(['git', 'checkout', tag_prefix + ver])
