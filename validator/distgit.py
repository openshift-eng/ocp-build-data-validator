import pygit2
from tempfile import TemporaryDirectory

from . import support


def validate(file, data, group_cfg):
    # Example url: git://pkgs.devel.redhat.com/containers/kuryr-cni.git
    namespace = support.get_namespace(data, file)
    repository = support.get_repository_name(file)
    distgit_host = 'pkgs.devel.redhat.com'
    repo_name = f'{namespace}/{repository}'
    repo_url = f'git://{distgit_host}/{namespace}/{repository}.git'
    branch = support.get_distgit_branch(data, group_cfg)

    if not support.resource_is_reachable(f'https://{distgit_host}'):
        return repo_url, f'This validation must run from a network with access to {distgit_host}'

    repo_dir = TemporaryDirectory()

    repo = make_repo(repo_name, repo_url, repo_dir.name)

    remote = repo.remotes[repo_name]

    if not repo_exists(remote):
        return repo_url, 'DistGit repository does not exist'

    if not branch_exists(remote, branch):
        return repo_url, f'Did not find {branch} in DistGit'

    return repo_url, None


def make_repo(name, url, repo_dir):
    repo = pygit2.init_repository(repo_dir)
    repo.remotes.create(name, url)
    return repo


def repo_exists(remote):
    try:
        remote.connect()
        return True
    except pygit2.GitError:
        return False


def branch_exists(remote, branch):
    remote_branches = remote.ls_remotes()
    ref = f'refs/heads/{branch}'
    branch_found = False

    for remote_branch in remote_branches:
        if remote_branch['name'] == ref:
            branch_found = True
            break
    return branch_found
