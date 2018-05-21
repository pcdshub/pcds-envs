import configparser
import contextlib
import os
import subprocess
import sys

import yaml

REPOS = ['pcdshub/happi',
         'pcdshub/hutch-python',
         'pcdshub/lightpath',
         'pcdshub/pcdsdaq',
         'pcdshub/pcdsdevices']


@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    yield
    os.chdir(previous_dir)


if __name__ == '__main__':
    filename = sys.argv[1]

    info = {}
    for repo in REPOS:
        org, pkg = repo.split('/')
        info[pkg] = {'repo': repo}

    with open(filename, 'r') as fd:
        yml = yaml.load(fd)

    for dep in yml['dependencies']:
        if isinstance(dep, str):
            pkg_name, ver = dep.split('=')
            if pkg_name in info:
                info[pkg_name]['ver'] = ver

    for pkg in info.keys():
        subprocess.run(['git', 'clone',
                        'https://github.com/{}'.format(info[pkg]['repo'])])
        with pushd(pkg):
            config = configparser.ConfigParser()
            config.read('setup.cfg')
            tag_prefix = config['versioneer']['tag_prefix']
            subprocess.run(['git', 'checkout', tag_prefix + info[pkg]['ver']])
