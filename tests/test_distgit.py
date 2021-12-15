import unittest
import pygit2
import mock

from validator import distgit


class TestDistGit(unittest.TestCase):
    def test_repo_does_not_exist(self):
        remote = mock.Mock()
        remote.connect = mock.Mock(side_effect=pygit2.GitError)
        self.assertFalse(distgit.repo_exists(remote))

    def test_repo_exist(self):
        remote = mock.Mock()
        self.assertTrue(distgit.repo_exists(remote))

    def test_branch_exists(self):
        remote = mock.Mock()
        remote.ls_remotes = mock.Mock(return_value=[{'name': 'abc'}, {'name': 'refs/heads/foo'}])
        self.assertTrue(distgit.branch_exists(remote, 'foo'))

    def test_branch_does_not_exist(self):
        remote = mock.Mock()
        remote.ls_remotes = mock.Mock(return_value=[{'name': 'abc'}, {'name': 'niceness'}])
        self.assertFalse(distgit.branch_exists(remote, 'foo'))
