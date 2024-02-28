"""
Exports the current environment, then fixes pypi git lines
"""
import argparse
import pathlib
import subprocess

parser = argparse.ArgumentParser("export_env.py")
parser.add_argument("--rel", type=str)
parser.add_argument("--base", type=str, default="pcds")


def main(base: str, rel: str) -> int:
    env_name = f"{args.base}-{args.rel}"
    env_dir = pathlib.Path(__file__).parent.parent / "envs" / args.base
    env_path = env_dir / "env.yaml"
    subprocess.run(["conda", "env", "export", "-n", env_name, "-f", str(env_path)], check=True)
    with env_path.open("r") as fd:
        yaml_lines = fd.read().splitlines()
    git_spec_path = env_dir / "git-packages.txt"
    with git_spec_path.open("r") as fd:
        git_lines = fd.read().splitlines()

    for line in git_lines:
        done = False
        line = line.strip()
        pkg, git_spec = line.split()
        for num, line in enumerate(yaml_lines):
            try:
                indent, spec = line.split("- ")
            except ValueError:
                # Not a spec line
                continue
            if spec.startswith(f"{pkg}=="):
                yaml_lines[num] = "- ".join((indent, git_spec))
                done = True
                break
        if not done:
            raise RuntimeError(f"Did not find {pkg} in yaml")

    # Supposed to end with a newline
    yaml_lines.append("")
    with env_path.open("w") as fd:
        fd.write("\n".join(yaml_lines))
    print(env_path)
    return 0


if __name__ == "__main__":
    args = parser.parse_args()
    exit(main(args.base, args.rel))
