import os
from . import support


def validate(file, data, group_cfg):
    endpoint = get_cgit_endpoint(group_cfg)
    namespace = get_namespace(data, support.get_artifact_type(file))
    repository = get_repository_name(file)

    url = '{}/{}/{}'.format(endpoint, namespace, repository)

    if not support.resource_is_reacheable(endpoint):
        return (url, ('This validation must run from a network '
                      'with access to {}'.format(endpoint)))

    if not support.resource_exists(url):
        return (url, ('Corresponding DistGit repo was not found.\n'
                      "If you didn't request a DistGit repo yet, "
                      'please check https://mojo.redhat.com/docs/DOC-1168290\n'
                      'But if you already obtained one, make sure its name '
                      'matches the YAML filename'))

    branch = get_distgit_branch(data, group_cfg)
    if not branch_exists(branch, url):
        return (url, ('Branch {} not found on DistGit'.format(branch)))

    return (url, None)


def get_cgit_endpoint(group_cfg):
    return group_cfg['urls']['cgit']


def get_namespace(data, artifact_type):
    if 'distgit' in data and 'namespace' in data['distgit']:
        return data['distgit']['namespace']

    return {'image': 'containers', 'rpm': 'rpms'}.get(artifact_type, '???')


def get_repository_name(file):
    return os.path.basename(file).split('.')[0]


def get_distgit_branch(data, group_cfg):
    if 'distgit' in data and 'branch' in data['distgit']:
        return data['distgit']['branch']

    return (group_cfg['branch']
            .replace('{MAJOR}', str(group_cfg['vars']['MAJOR']))
            .replace('{MINOR}', str(group_cfg['vars']['MINOR'])))


def branch_exists(branch, url):
    return support.resource_exists('{}/log?h={}'.format(url, branch))
