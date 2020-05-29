from validator import support
from validator import __main__


def validate(data, group_cfg):
    if not has_declared_github_repository(data):
        return None, None

    url = get_repository_url(data)

    if not support.resource_exists(url):
        return url, "GitHub repository {} doesn't exist".format(url)

    if not has_declared_branches(data):
        return url, 'No branches specified under content > source > git'

    (target, fallback) = get_branches(data, group_cfg)

    if not branch_exists(target, url, __main__.token) and \
            not branch_exists(fallback, url, __main__.token):
        return (url, ('At least one of the following branches should exist: '
                      '{} or {}'.format(target, fallback)))

    branch = target if branch_exists(target, url, __main__.token) else fallback

    if has_declared_dockerfile(data):
        dockerfile = get_dockerfile(data)

        if not file_exists_on_repo(dockerfile, url, branch, __main__.token):
            return (url, ('dockerfile {} not found on branch {}'
                          .format(dockerfile, branch)))

    if has_declared_manifests(data):
        manifests = get_manifests_dir(data)

        if not file_exists_on_repo(manifests, url, branch, __main__.token):
            return (url, ('manifests {} not found on branch {}'
                          .format(manifests, branch)))

    return url, None


def has_declared_github_repository(data):
    return ('content' in data
            and 'source' in data['content']
            and 'git' in data['content']['source']
            and 'url' in data['content']['source']['git'])


def get_repository_url(data):
    return (data['content']['source']['git']['url']
            .replace('git@github.com:', 'https://github.com/')
            .replace('.git', ''))


def has_declared_branches(data):
    return ('content' in data
            and 'source' in data['content']
            and 'git' in data['content']['source']
            and 'branch' in data['content']['source']['git']
            and ('target' in data['content']['source']['git']['branch']
                 or 'fallback' in data['content']['source']['git']['branch']))


def get_branches(data, group_cfg):
    branch = data['content']['source']['git']['branch']
    target = (branch.get('target')
              .replace('{MAJOR}', str(group_cfg['vars']['MAJOR']))
              .replace('{MINOR}', str(group_cfg['vars']['MINOR'])))
    fallback = branch.get('fallback')
    return target, fallback


# if token exist use Github API
# https://developer.github.com/v3/repos/branches/#get-branch
# GET /repos/:owner/:repo/branches/:branch
def branch_exists(branch, url, token):
    if token is None:
        return support.resource_exists('{}/tree/{}'.format(url, branch))
    else:
        return support.resource_exists(
            '{}/branches/{}'.format(url, branch))


def has_declared_dockerfile(data):
    return ('content' in data
            and 'source' in data['content']
            and 'dockerfile' in data['content']['source'])


def get_dockerfile(data):
    path = '{}/'.format(get_custom_path(data)) if has_custom_path(data) else ''
    return '{}{}'.format(path, data['content']['source']['dockerfile'])


def has_custom_path(data):
    return ('content' in data
            and 'source' in data['content']
            and 'path' in data['content']['source'])


def get_custom_path(data):
    return data['content']['source']['path']


# if token exist then using github API
# https://developer.github.com/v3/repos/contents/#get-contents
# GET /repos/:owner/:repo/contents/:path
def file_exists_on_repo(dockerfile, url, branch, token):
    if token is None:
        dockerfile_url = '{}/blob/{}/{}'.format(url, branch, dockerfile)
    else:
        dockerfile_url = \
            '{}/contents/{}/?ref={}'.format(url, dockerfile, branch)
    return support.resource_exists(dockerfile_url)


def has_declared_manifests(data):
    return 'update-csv' in data and 'manifests-dir' in data['update-csv']


def get_manifests_dir(data):
    path = '{}/'.format(get_custom_path(data)) if has_custom_path(data) else ''
    return '{}{}'.format(path, data['update-csv']['manifests-dir'])
