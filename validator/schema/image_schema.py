from validator import support
from schema import Schema, Optional, And, Or, Regex, SchemaError
from validator.schema.modification_schema import modification

GIT_SSH_URL_REGEX = r'((git@[\w\.]+))([\w\.@\:/\-~]+)(\.git)(/)?'

IMAGE_CONTENT_SCHEMA = {
    'source': {
        Optional('alias'): And(str, len),
        Optional('ci_alignment'): {
            # Default (Missing) == true.
            Optional('enabled'): bool,
            # parameter for the transform Dockerfile to set this user when complete
            Optional('final_user'): Or(str, int),
            # mirror this image for CI to use
            Optional('mirror'): bool,
            # configuration for creating PRs to align upstream dockerfiles w/ ART
            Optional('streams_prs'): {
                # Explicitly override the buildroot to be used for CI tests
                Optional('ci_build_root'): {
                    'stream': And(str, len),
                },
                # Default (Missing) == true.
                Optional('enabled'): bool,
                # automatically add labels to alignment PRs when created
                Optional('auto_label'): [And(str, len)],
                # Explicitly override the FROMs to be used upstream:
                Optional('from'): [And(str, len)],
                # merge_first means that child images will not get PRs opened
                # until this image is aligned. This helps prevent images like
                # openshift's base image from having 100s of PRs referencing
                # its PR.
                Optional('merge_first'): bool,
                # commit_prefix will add a prefix to the commit msg in ART alignment PRs
                Optional('commit_prefix'): str,
            },
            # when mirroring a base image for CI, we push and transform:
            # run a build to add a layer (typically to add repos)
            Optional('transform'): And(str, len),
            # transformed image landing point; streams_pr will use this as FROM
            Optional('upstream_image'): And(str, len),
            # push the ART image here; transform is applied to it
            Optional('upstream_image_base'): And(str, len),
        },
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
        Optional(Or('pkg_managers', 'pkg_managers!')): [
            And(str, len, lambda s: s in ('gomod',)),
        ],
    },
}


def image_schema(file):
    valid_arches = [
        'x86_64',
        's390x',
        'ppc64le',
        'aarch64',
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
        Optional('content'): IMAGE_CONTENT_SCHEMA,
        Optional('dependents'): [
            And(str, len)
        ],
        Optional('distgit'): {
            Optional('namespace'): Or(*valid_distgit_namespaces),
            Optional('component'): And(str, len),
            Optional('bundle_component'): And(str, len),
            Optional('branch'): And(str, len),
        },
        # When doozer injects USER 0 to do a yum update, this
        # field instructs doozer to set this user afterwards
        # in the final stage of the build.
        Optional('final_stage_user'): Or(str, int),
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
            Optional('summary'): And(str, len),
            Optional('License'): And(str, len),
            Optional('com.redhat.delivery.appregistry'): Or(bool, "true", "false"),
            Optional('io.k8s.description'): And(str, len),
            Optional('io.k8s.display-name'): And(str, len),
            Optional('io.openshift.release.operator'): And(str, len),
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
        Optional('payload_name'): And(str, len),
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
        Optional('name_in_bundle'): And(str, len),
    })


def validate(file, data):
    try:
        image_schema(file).validate(data)
    except SchemaError as err:
        return '{}'.format(err)
