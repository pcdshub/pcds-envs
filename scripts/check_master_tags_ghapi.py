import pathlib
import sys
from ghapi.all import GhApi

api = GhApi()

def is_tag_latest(org: str = 'pcdshub', repo: str = ""):
    """Returns true if the latest commit matches that of the latest tag"""

    if not repo:
        return False

    last_commit = api.repos.list_commits(org, repo, per_page=1)[0]
    last_commit_sha = last_commit['sha']

    last_tag = api.repos.list_tags(org, repo, per_page=1)[0]
    last_tag_sha = last_tag['commit']['sha']

    if last_commit_sha == last_tag_sha:
        return last_tag['name']
    
    return False


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

    max_out_length = 0
    for i, repo in enumerate(repos):
        org, repository_name = repo.split('/')
        out_string = f"checking {repo} ({i+1}/{len(repos)})"
        if len(out_string) > max_out_length:
            max_out_length = len(out_string)

        print(out_string + " " * (max_out_length - len(out_string)), end="\r")
        latest_tag = is_tag_latest(org, repository_name)
        if not latest_tag:
            untagged.append(repo)
        else:
            tagged[repo] = latest_tag

    print(" " * max_out_length)
    for repo, tag in tagged.items():
        print(f'{repo} is tagged at {tag}')

    print()
    for repo in untagged:
        print(f'{repo} is not tagged')

if __name__ == "__main__":
    main()