from validator import support
from schema import Schema, Optional, Use, And, Or, SchemaError


def image_schema(file):
    valid_arches = [
        'x86_64',
    ]

    valid_modification_actions = [
        'command',
        'replace',
    ]

    valid_modification_commands = [
        'update-console-sources',
    ]

    valid_distgit_namespaces = [
        'apbs',
        'containers',
        'rpms',
    ]

    valid_streams = support.get_valid_streams_for(file)
    valid_member_references = support.get_valid_member_references_for(file)

    valid_modes = [
        'auto',
        'disabled',
        'wip',
    ]

    return Schema({
        Optional('arches'): [Or(*valid_arches)],
        Optional('base_only'): True,
        Optional('container_yaml'): {
            'go': {
                'modules': [
                    {
                        'module': And(str, len),
                        Optional('path'): str,
                    },
                ],
            },
        },
        Optional('content'): {
            'source': {
                Optional('alias'): And(str, len),
                Optional('dockerfile'): And(str, len),
                Optional('git'): {
                    'branch': {
                        Optional('fallback'): And(str, len),
                        'target': And(str, len),
                    },
                    'url': And(Use(str), len),
                },
                Optional('modifications'): [{
                    'action': Or(*valid_modification_actions),
                    Optional('command'): [
                        Or(*valid_modification_commands),
                    ],
                    Optional('match'): And(str, len),
                    Optional('replacement'): And(str, len),
                }],
                Optional('path'): str,
            },
        },
        Optional('dependents'): [
            And(str, len)
        ],
        Optional('distgit'): {
            Optional('namespace'): Or(*valid_distgit_namespaces),
            Optional('component'): And(str, len),
            Optional('branch'): And(str, len),
        },
        Optional('enabled_repos'): [
            And(str, len),
        ],
        'from': {
            Optional('builder'): [
                {
                    Optional('stream'): Or(*valid_streams),
                    Optional('member'): Or(*valid_member_references),
                    Optional('image'): And(str, len),
                },
            ],
            Optional('image'): And(str, len),
            Optional('stream'): Or(*valid_streams),
            Optional('member'): Or(*valid_member_references),
        },
        Optional('labels'): {
            Optional('License'): And(str, len),
            Optional('io.k8s.description'): And(str, len),
            Optional('io.k8s.display-name'): And(str, len),
            Optional('io.openshift.tags'): And(str, len),
            Optional('vendor'): And(str, len),
        },
        Optional('mode'): Or(*valid_modes),
        'name': And(str, len),
        Optional('odcs'): {
            'packages': {
                'exclude': [
                    And(str, len),
                ],
                'mode': 'auto',
            },
        },
        Optional('no_oit_comments'): bool,
        Optional('owners'): [
            And(str, len),
        ],
        Optional('push'): {
            'repos': [
                And(str, len),
            ],
        },
        Optional('required'): bool,
        Optional('update-csv'): {
            'manifests-dir': And(str, len),
            'registry': And(str, len),
        },
        Optional('wait_for'): And(str, len),
    })


def validate(file, data):
    try:
        image_schema(file).validate(data)
    except SchemaError as err:
        return '{}'.format(err)
