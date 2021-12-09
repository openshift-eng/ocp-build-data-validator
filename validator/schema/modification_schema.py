from schema import Schema, Optional, And, Or


def modification(file):
    valid_modification_actions = [
        'command',
        'replace',
        'add',
    ]

    valid_modification_commands = [
        'update-console-sources',
        'update-jenkins-label',
        'upload-coreos-iso-to-lookaside-cache',
    ]
    return Schema({
                  'action': Or(*valid_modification_actions),
                  Optional('command'): [
                      Or(*valid_modification_commands),
                  ],
                  Optional('match'): And(str, len),
                  Optional('replacement'): Or(None, str),
                  Optional('source'): And(str, len),
                  Optional('path'): And(str, len),
                  Optional('overwriting'): bool,
                  }).validate(file)
