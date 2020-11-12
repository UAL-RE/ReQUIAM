from pathlib import Path
from os.path import join, exists


def get_active_branch_name(input_path="."):

    if exists(join(input_path, ".git", "HEAD")):
        head_dir = Path(input_path) / ".git" / "HEAD"
        with head_dir.open("r") as f:
            content = f.read().splitlines()

        for line in content:
            if line[0:4] == "ref:":
                return line.partition("refs/heads/")[2]
    else:
        return '.git structure does not exist'


def get_latest_commit(input_path="."):

    if exists(join(input_path, ".git", "HEAD")):
        head_dir = Path(input_path) / ".git" / "HEAD"
        with head_dir.open("r") as f:
            content = f.read().splitlines()

        for line in content:
            if line[0:4] == "ref:":
                head_path = Path(f".git/{line.partition(' ')[2]}")
                with head_path.open('r') as g:
                    commit = g.read().splitlines()

        return commit[0], commit[0][:7]  # full and short hash
    else:
        return '.git structure does not exist', ''
