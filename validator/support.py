import os
import requests
import yaml

from . import exceptions
from . import global_session


def fail_validation(msg, parsed):
    if 'mode' in parsed and parsed['mode'] == 'wip':
        raise exceptions.ValidationFailedWIP(msg)
    raise exceptions.ValidationFailed(msg)


def is_disabled(parsed):
    return 'mode' in parsed and parsed['mode'] == 'disabled'


def load_group_config_for(file):
    group_yaml = os.path.join(get_ocp_build_data_dir(file), 'group.yml')
    return yaml.safe_load(open(group_yaml).read())


def get_ocp_build_data_dir(file):
    return os.path.normpath(os.path.join(os.path.dirname(file), '..'))


def get_artifact_type(file):
    if 'images/' in file:
        return 'image'

    if 'rpms/' in file:
        return 'rpm'

    return '???'


def get_valid_streams_for(file):
    streams_yaml = os.path.join(get_ocp_build_data_dir(file), 'streams.yml')
    return set(yaml.safe_load(open(streams_yaml).read()).keys())


def get_valid_member_references_for(file):
    images_dir = os.path.join(get_ocp_build_data_dir(file), 'images')
    return set([os.path.splitext(img)[0] for img in os.listdir(images_dir)])


def resource_exists(url):
    if url.startswith('https://github.com/openshift/ose-ovn-kubernetes'):
        # This is a private repository, and only used for 3.11. This will not change.
        return True
    if global_session.request_session:
        return 200 <= global_session.request_session\
            .head(url).status_code < 400
    else:
        return 200 <= requests.head(url).status_code < 400


def resource_is_reacheable(url):
    try:
        requests.head(url)
        return True
    except requests.exceptions.ConnectionError:
        return False
