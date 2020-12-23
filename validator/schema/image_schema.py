from validator import support
from schema import Schema, Optional, And, Or, Regex, SchemaError
from validator.schema.modification_schema import modification

GIT_SSH_URL_REGEX = r'((git@[\w\.]+))([\w\.@\:/\-~]+)(\.git)(/)?'


def image_schema(file):
    valid_arches = [
        'x86_64',
        'ppc64le',
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

    valid_odcs_modes = [
        'auto',
        'manual',
    ]

    return Schema({
        Optional('additional_tags'): [
            And(str, len),
        ],
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
                        Optional('stage'): And(str, len),
                        'target': And(str, len),
                    },
                    'url': And(str, len, Regex(GIT_SSH_URL_REGEX)),
                },
                Optional('modifications'): [modification],
                Optional('path'): str,
                Optional('pkg_managers'): [
                    And(str, len, lambda s: s in ('gomod',)),
                ],
                Optional('ci_alignment'): {
                    Optional('streams_prs'): {
                        # Default (Missing) == true.
                        Optional('enabled'): bool,
                        'auto_label': [
                            And(str, len),
                        ],
                        # merge_first means that child images will not get PRs opened
                        # until this image is aligned. This helps prevent images like
                        # openshift's base image from having 100s of PRs referencing
                        # its PR.
                        Optional('merge_first'): bool,
                    },
                },
            },
        },
        Optional('dependents'): [
            And(str, len)
        ],
        Optional('distgit'): {
            Optional('namespace'): Or(*valid_distgit_namespaces),
            Optional('component'): And(str, len),
            Optional('bundle_component'): And(str, len),
            Optional('branch'): And(str, len),
        },
        Optional('enabled_repos'): [
            And(str, len),
        ],
        Optional('non_shipping_repos'): [
            And(str, len),
        ],
        Optional('non_shipping_rpms'): [
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
        Optional('image_build_method'): And(str, len),
        Optional('mode'): Or(*valid_modes),
        'name': And(str, len),
        Optional('odcs'): {
            'packages': {
                Optional('exclude'): [
                    And(str, len),
                ],
                Optional('list'): [
                    And(str, len),
                ],
                'mode': Or(*valid_odcs_modes),
            },
        },
        Optional('no_oit_comments'): bool,
        Optional('owners'): [
            And(str, len),
        ],
        Optional('push'): {
            Optional('repos'): [
                And(str, len),
            ],
            Optional('additional_tags'): [
                And(str, len),
            ],
            Optional('late'): bool,
        },
        Optional('required'): bool,
        Optional('scan_sources'): {
            Optional('extra_packages'): [
                {
                    'name': And(str, len),
                    'tag': And(str, len),
                },
            ],
        },
        Optional('update-csv'): {
            'manifests-dir': And(str, len),
            'bundle-dir': And(str, len),
            'registry': And(str, len),
            Optional('channel'): And(str, len),
            Optional('image-map'): dict,
        },
        Optional('wait_for'): And(str, len),
        Optional('maintainer'): {
            Optional('product'): And(str, len),
            'component': And(str, len),
            Optional('subcomponent'): And(str, len),
        },
        Optional('for_payload'): bool,
        Optional('for_release'): bool,
    })


def validate(file, data):
    try:
        image_schema(file).validate(data)
    except SchemaError as err:
        return '{}'.format(err)
