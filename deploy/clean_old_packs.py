"""
Script to clean up old conda pack relics
"""
import argparse
import os
import os.path
import re
import shutil
import socket
from dataclasses import dataclass
from typing import List, Tuple

HUTCH_PYTHON_ENV = '/cds/group/pcds/pyps/apps/hutch-python/{hutch}/{hutch}env'
UNPACK_DIRECTORY = '/u1/{hutch}opr/conda_envs'
VER_MATCH = re.compile(r'^[^#].*CONDA_ENVNAME.*pcds-(\d\.\d\.\d)')


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


def get_current_hutch() -> str:
    """
    Quick and simple: get the hutch name from our server name.
    """
    hostname = socket.gethostname()
    return hostname.split('-')[0]


def envs_to_keep(hutch: str):
    current_version = get_current_version(hutch)
    all_envs = get_saved_envs(hutch)
    keep = all_envs[-5:]
    found_current_version = False
    for env in all_envs:
        if env.version == current_version:
            if env not in keep:
                keep.insert(0, env)
            found_current_version = True
            break
    if not found_current_version:
        raise RuntimeError('Did not find current version installed, something is wrong.')
    return keep


def envs_to_remove(hutch: str, keep: List[UnpackedEnv]):
    all_paths = get_saved_envs(hutch)
    return [path for path in all_paths if path not in keep]


def main(dry_run=True):
    print('Cleaning up old hutch python directories.')
    hutch = get_current_hutch()
    keep = envs_to_keep(hutch)
    remove = envs_to_remove(hutch, keep)
    current_ver = get_current_version(hutch)
    print(f'Current version is {current_ver}')
    if keep:
        print('Keeping the following envs:')
        for env in keep:
            print(env)
    if remove:
        print('Remove the following envs:')
        for env in remove:
            print(env)
    else:
        print('Did not find any paths to clean up')
        return
    if dry_run:
        print('Dry run: not deleting envs')
    else:
        for env in remove:
            print(f'Deleting {env}')
            shutil.rmtree(env.path)


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
