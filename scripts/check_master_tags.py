# Helper script to check which packages we need to tag
import os
import pathlib
import shutil
import subprocess
import sys
import time


def get_master_tag(repo):
    tmp_dir = 'check_tag_tmp'
    shutil.rmtree(tmp_dir, ignore_errors=True)

    clone_tries = 10
    while clone_tries > 0:
        try:
            subprocess.run(['git', 'clone', '--depth', '1', f'https://github.com/{repo}',
                            tmp_dir], check=True)
            break
        except subprocess.CalledProcessError:
            time.sleep(5)
            clone_tries -= 1
            if clone_tries <= 0:
                raise

    os.chdir(tmp_dir)
    try:
        tag = subprocess.check_output(['git', 'describe', '--tags'],
                                      universal_newlines=True)
        tag = tag.strip()
    except subprocess.CalledProcessError:
        tag = ''
    os.chdir('..')
    shutil.rmtree(tmp_dir)
    return tag


def collect_repos(filename):
    with open(filename, 'r') as fd:
        return fd.read().splitlines()


def main():
    try:
        env = sys.argv[1]
    except Exception:
        env = 'pcds'

    here = pathlib.Path(__file__).resolve().parent
    test_repos_file = here.parent / 'envs' / env / 'package-tests.txt'

    repos = collect_repos(test_repos_file)
    tagged = {}
    untagged = []

    for repo in repos:
        tag = get_master_tag(repo)
        if tag:
            tagged[repo] = tag
        else:
            untagged.append(repo)

    print()
    for repo, tag in tagged.items():
        print(f'{repo} is tagged at {tag}')

    print()
    for repo in untagged:
        print(f'{repo} is not tagged')


if __name__ == '__main__':
    main()
