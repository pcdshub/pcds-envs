"""
Script to clean up old conda pack relics
"""
from dataclasses import dataclass
from typing import Tuple, List
import argparse
import os
import os.path
import re
import shutil
import socket
import sys


HUTCH_PYTHON_ENV = '/cds/group/pcds/pyps/apps/hutch-python/{hutch}/{hutch}env'
UNPACK_DIRECTORY = '/u1/{hutch}opr/conda_envs'
VER_MATCH = re.compile('^[^#].*CONDA_ENVNAME.*pcds-(\d\.\d\.\d)')


@dataclass
class UnpackedEnv:
    version: Tuple[int, int, int]
    path: str


def get_current_version(hutch: str) -> Tuple[int, int, int]:
    """
    For a given hutch, which version is being run?

    Parameters
    ----------
    hutch : str
        The hutch we're in.

    Returns
    -------
    version : tuple of int
        The version numbers associated with the current version,
        (major, minor, bugfix)
    """
    with open(HUTCH_PYTHON_ENV.format(hutch=hutch), 'r') as fd:
        lines = fd.read().splitlines()

    for line in lines:
        match = VER_MATCH.match(line)
        if match:
            group = match.group(1)
            return tuple(int(num) for num in group.split('.'))


def get_saved_envs(hutch: str) -> List[UnpackedEnv]:
    """
    For a given hutch, get which conda envs are saved on the hard drive.

    Parameters
    ----------
    hutch : str
        The hutch we're in.
    buffer : int, optional
        How many extra environments prior to the current env to keep.

    Returns
    -------
    envs : list of UnpackedEnv
        The environments we found.
    """
    directory = UNPACK_DIRECTORY.format(hutch=hutch)
    filenames = os.listdir(directory)
    output = []
    for fname in filenames:
        ver = fname.split('-')[1]
        ver_tuple = tuple(int(num) for num in ver.split('.'))
        output.append(
            UnpackedEnv(
                version=ver_tuple,
                path=os.path.join(directory, fname),
            )
        )
    return sorted(
        output,
        key=lambda x: x.version,
    )


def get_older_paths(hutch: str, buffer: int = 5) -> List[str]:
    """
    For a given hutch, get paths that are OK to delete.

    Parameters
    ----------
    hutch : str
        The hutch we're in.
    buffer : int, optional
        How many extra environments prior to the current env to keep.

    Returns
    -------
    paths : list of str
        All the paths that are OK to delete.
    """
    current_version = get_current_version(hutch)
    saved_envs = get_saved_envs(hutch)
    old_envs = []
    for env in reversed(saved_envs):
        if env.version >= current_version:
            continue
        if buffer > 0:
            buffer -= 1
        else:
            old_envs.append(env.path)
    return list(reversed(old_envs))


def get_current_hutch() -> str:
    """
    Quick and simple: get the hutch name from our server name.
    """
    hostname = socket.gethostname()
    return hostname.split('-')[0]


def main(dry_run=True):
    print('Cleaning up old hutch python directories.')
    hutch = get_current_hutch()
    paths = get_older_paths(hutch)
    if not paths:
        print('Did not find any paths to clean up')
        return
    print(f'Found old paths: {paths}')
    if dry_run:
        print('Dry run: not deleting paths')
    else:
        for path in paths:
            print(f'Deleting {path}')
            # shutil.rmtree(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Remove old hutch python directories to save disk space',
    )
    parser.add_argument(
        '--delete',
        action='store_true',
        help='Set this flag to delete files instead of doing a dry run.',
    )
    args = parser.parse_args()
    main(dry_run=not args.delete)

