import unittest
import flexmock
from validator import github


class TestGitHub(unittest.TestCase):

    def setUp(self):
        (flexmock(github.support)
            .should_receive('resource_exists')
            .and_return(True))

    def test_no_declared_repository(self):
        (url, err) = github.validate({}, {})
        self.assertIsNone(url)
        self.assertIsNone(err)

    def test_repository_doesnt_exist(self):
        (flexmock(github.support)
            .should_receive('resource_exists')
            .with_args('https://github.com/myorg/myrepo')
            .and_return(False))

        data = {
            'content': {
                'source': {
                    'git': {
                        'url': 'https://github.com/myorg/myrepo',
                    }
                }
            }
        }

        (url, err) = github.validate(data, {})
        self.assertEqual(url, 'https://github.com/myorg/myrepo')
        self.assertEqual(err, ('GitHub repository '
                               "https://github.com/myorg/myrepo doesn't "
                               'exist'))

    def test_no_declared_branches(self):
        data = {
            'content': {
                'source': {
                    'git': {
                        'url': 'https://github.com/myorg/myrepo',
                    }
                }
            }
        }

        (url, err) = github.validate(data, {})
        self.assertEqual(url, 'https://github.com/myorg/myrepo')
        self.assertEqual(err, ('No branches specified under '
                               'content > source > git'))

    def test_target_branch_doesnt_exist(self):
        (flexmock(github)
            .should_receive('branch_exists')
            .with_args('release-4.2', 'https://github.com/myorg/myrepo')
            .and_return(False))

        (flexmock(github)
            .should_receive('branch_exists')
            .with_args('fallback-branch', 'https://github.com/myorg/myrepo')
            .and_return(True))

        data = {
            'content': {
                'source': {
                    'git': {
                        'branch': {
                            'target': 'release-{MAJOR}.{MINOR}',
                            'fallback': 'fallback-branch',
                        },
                        'url': 'https://github.com/myorg/myrepo',
                    }
                }
            }
        }

        (url, err) = github.validate(data, {'vars': {'MAJOR': 4, 'MINOR': 2}})
        self.assertEqual(url, 'https://github.com/myorg/myrepo')
        self.assertEqual(err, None)

    def test_target_nor_fallback_branches_exist(self):
        (flexmock(github)
            .should_receive('branch_exists')
            .with_args('release-4.2', 'https://github.com/myorg/myrepo')
            .and_return(False))

        (flexmock(github)
            .should_receive('branch_exists')
            .with_args('fallback-branch', 'https://github.com/myorg/myrepo')
            .and_return(False))

        data = {
            'content': {
                'source': {
                    'git': {
                        'branch': {
                            'target': 'release-{MAJOR}.{MINOR}',
                            'fallback': 'fallback-branch',
                        },
                        'url': 'https://github.com/myorg/myrepo',
                    }
                }
            }
        }

        (url, err) = github.validate(data, {'vars': {'MAJOR': 4, 'MINOR': 2}})
        self.assertEqual(url, 'https://github.com/myorg/myrepo')
        self.assertEqual(err, ('At least one of the following branches '
                               'should exist: release-4.2 or fallback-branch'))

    def test_declared_dockerfile_doesnt_exist(self):
        (flexmock(github.support)
            .should_receive('resource_exists')
            .with_args('https://github.com/org/repo/blob/xyz/Dockerfile.rhel7')
            .and_return(False))

        data = {
            'content': {
                'source': {
                    'dockerfile': 'Dockerfile.rhel7',
                    'git': {
                        'branch': {
                            'target': 'xyz',
                            'fallback': 'fallback-branch',
                        },
                        'url': 'https://github.com/org/repo',
                    }
                }
            }
        }

        (url, err) = github.validate(data, {'vars': {'MAJOR': 4, 'MINOR': 2}})
        self.assertEqual(url, 'https://github.com/org/repo')
        self.assertEqual(err, ('dockerfile Dockerfile.rhel7 '
                               'not found on branch xyz'))

    def test_declared_dockerfile_on_custom_path(self):
        bad_file_url = 'https://github.com/org/repo/blob/xyz/Dockerfile.rhel7'
        (flexmock(github.support)
            .should_receive('resource_exists')
            .with_args(bad_file_url)
            .and_return(False))

        good_file_url = ('https://github.com/org/repo/blob/xyz/my/custom/path/'
                         'Dockerfile.rhel7')
        (flexmock(github.support)
            .should_receive('resource_exists')
            .with_args(good_file_url)
            .and_return(True))

        data = {
            'content': {
                'source': {
                    'dockerfile': 'Dockerfile.rhel7',
                    'git': {
                        'branch': {
                            'target': 'xyz',
                            'fallback': 'fallback-branch',
                        },
                        'url': 'https://github.com/org/repo',
                    },
                    'path': 'my/custom/path',
                }
            }
        }

        (url, err) = github.validate(data, {'vars': {'MAJOR': 4, 'MINOR': 2}})
        self.assertEqual(url, 'https://github.com/org/repo')
        self.assertIsNone(err)

    def test_declared_manifest_doesnt_exist(self):
        (flexmock(github.support)
            .should_receive('resource_exists')
            .with_args('https://github.com/org/repo/blob/xyz/my-manifests')
            .and_return(False))

        data = {
            'content': {
                'source': {
                    'git': {
                        'branch': {
                            'target': 'xyz',
                            'fallback': 'fallback-branch',
                        },
                        'url': 'https://github.com/org/repo',
                    }
                }
            },
            'update-csv': {
                'manifests-dir': 'my-manifests',
            },
        }

        (url, err) = github.validate(data, {'vars': {'MAJOR': 4, 'MINOR': 2}})
        self.assertEqual(url, 'https://github.com/org/repo')
        self.assertEqual(err, 'manifests my-manifests not found on branch xyz')

    def test_declared_manifest_on_custom_path(self):
        bad_file_url = 'https://github.com/org/repo/blob/xyz/my-manifests'
        (flexmock(github.support)
            .should_receive('resource_exists')
            .with_args(bad_file_url)
            .and_return(False))

        good_file_url = ('https://github.com/org/repo/blob/xyz/my/custom/path/'
                         'my-manifests')
        (flexmock(github.support)
            .should_receive('resource_exists')
            .with_args(good_file_url)
            .and_return(True))

        data = {
            'content': {
                'source': {
                    'git': {
                        'branch': {
                            'target': 'xyz',
                            'fallback': 'fallback-branch',
                        },
                        'url': 'https://github.com/org/repo',
                    },
                    'path': 'my/custom/path',
                }
            },
            'update-csv': {
                'manifests-dir': 'my-manifests',
            },
        }

        (url, err) = github.validate(data, {'vars': {'MAJOR': 4, 'MINOR': 2}})
        self.assertEqual(url, 'https://github.com/org/repo')
        self.assertIsNone(err)

    def test_complete_example(self):
        data = {
            'content': {
                'source': {
                    'dockerfile': 'Dockerfile.rhel7',
                    'git': {
                        'branch': {
                            'target': 'xyz',
                            'fallback': 'fallback-branch',
                        },
                        'url': 'https://github.com/org/repo',
                    }
                }
            },
            'update-csv': {
                'manifests-dir': 'my-manifests',
            },
        }

        (url, err) = github.validate(data, {'vars': {'MAJOR': 4, 'MINOR': 2}})
        self.assertEqual(url, 'https://github.com/org/repo')
        self.assertIsNone(err)

    def test_private_org_example(self):
        data = {
            'content': {
                'source': {
                    'dockerfile': 'Dockerfile.rhel7',
                    'git': {
                        'branch': {
                            'target': 'xyz',
                            'fallback': 'fallback-branch',
                        },
                        'url': 'https://github.com/openshift-priv/repo',
                    }
                }
            },
            'update-csv': {
                'manifests-dir': 'my-manifests',
            },
        }

        (url, err) = github.validate(data, {"vars": {
            "MAJOR": 4,
            "MINOR": 2
        },
            "public_upstreams": [
            {
                "private": "https://github.com/openshift-priv",
                "public": "https://github.com/openshift",
                "public_branch": "release-4.2"
            },
            {
                "private": "https://github.com/openshift/ose",
                "public": "https://github.com/openshift/origin",
                "public_branch": "release-4.2"
            }
        ]})
        self.assertEqual(url, 'https://github.com/openshift/repo')
        self.assertIsNone(err)
