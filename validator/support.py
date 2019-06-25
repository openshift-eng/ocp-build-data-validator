import os
import requests
import yaml


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
    return 200 <= requests.head(url).status_code < 400


def resource_is_reacheable(url):
    try:
        requests.head(url)
        return True
    except requests.exceptions.ConnectionError:
        return False
