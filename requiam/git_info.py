from pathlib import Path
from os.path import dirname, basename, exists, join

# Get git root
git_root = dirname(__file__.replace(f'/{basename(__file__)}', ''))


class GitInfo:
    def __init__(self, input_path: str = git_root):
        self.input_path = input_path
        self.branch = self.get_active_branch_name()
        commit_tuple = self.get_latest_commit()
        self.commit = commit_tuple[0]
        self.short_commit = commit_tuple[1]

    def get_active_branch_name(self):

        if exists(join(self.input_path, ".git", "HEAD")):
            head_dir = Path(self.input_path) / ".git" / "HEAD"
            with head_dir.open("r") as f:
                content = f.read().splitlines()

            for line in content:
                if line[0:4] == "ref:":
                    return line.partition("refs/heads/")[2]
                else:
                    return f"HEAD detached : {content[0]}"
        else:
            return '.git structure does not exist'

    def get_latest_commit(self):

        if exists(join(self.input_path, ".git", "HEAD")):
            head_dir = Path(self.input_path) / ".git" / "HEAD"
            with head_dir.open("r") as f:
                content = f.read().splitlines()

            for line in content:
                if line[0:4] == "ref:":
                    head_path = Path(join(self.input_path, f".git/{line.partition(' ')[2]}"))
                    with head_path.open('r') as g:
                        commit = g.read().splitlines()
                else:
                    commit = content

            return commit[0], commit[0][:7]  # full and short hash
        else:
            return '.git structure does not exist', ''
