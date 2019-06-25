from __future__ import print_function
import sys

from . import format, support, schema, github, distgit


def main():
    file = sys.argv[1]

    print('Validating {}'.format(file))

    (parsed, err) = format.validate(open(file).read())
    if err:
        print('{} is not a valid YAML'.format(file), file=sys.stderr)
        print('Returned error: {}'.format(err), file=sys.stderr)
        exit(1)

    err = schema.validate(file, parsed)
    if err:
        print('schema mismatch: {}'.format(file), file=sys.stderr)
        print('Returned error: {}'.format(err), file=sys.stderr)
        exit(1)

    group_cfg = support.load_group_config_for(file)

    (url, err) = github.validate(parsed, group_cfg)
    if err:
        print('GitHub validation failed for {}'.format(url), file=sys.stderr)
        print('Returned error: {}'.format(err, file=sys.stderr))
        exit(1)

    (url, err) = distgit.validate(file, parsed, group_cfg)
    if err:
        print('DistGit validation failed for {}'.format(url), file=sys.stderr)
        print('Returned error: {}'.format(err, file=sys.stderr))
        exit(1)
