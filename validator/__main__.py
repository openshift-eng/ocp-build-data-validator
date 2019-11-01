from __future__ import print_function
from multiprocessing import Pool, cpu_count
import argparse
import sys

from . import format, support, schema, github, distgit


def validate(file):
    print('Validating {}'.format(file))

    (parsed, err) = format.validate(open(file).read())
    if err:
        msg = '{} is not a valid YAML\nReturned error: {}'.format(file, err)
        support.fail_validation(msg, parsed)

    if support.is_disabled(parsed):
        print('Skipping validation of disabled {}.'.format(file))
        return

    err = schema.validate(file, parsed)
    if err:
        msg = 'Schema mismatch: {}\nReturned error: {}'.format(file, err)
        support.fail_validation(msg, parsed)

    group_cfg = support.load_group_config_for(file)

    (url, err) = github.validate(parsed, group_cfg)
    if err:
        msg = ('GitHub validation failed for {} ({})\n'
               'Returned error: {}').format(file, url, err)
        support.fail_validation(msg, parsed)

    (url, err) = distgit.validate(file, parsed, group_cfg)
    if err:
        msg = ('DistGit validation failed for {} ({})\n'
               'Returned error: {}').format(file, url, err)
        support.fail_validation(msg, parsed)


def main():
    parser = argparse.ArgumentParser(
        description='Validation of ocp-build-data Image & RPM declarations')
    parser.add_argument('files',
                        metavar='FILE',
                        type=str,
                        nargs='+',
                        help='Files to be validated')
    parser.add_argument('-s',
                        '--single-thread',
                        dest='single_thread',
                        default=False,
                        action='store_true',
                        help='Run in single thread, so code.interact() works')
    args = parser.parse_args()

    if args.single_thread:
        for f in args.files:
            validate(f)
    else:
        try:
            Pool(cpu_count()).map(validate, args.files)
        except Exception as e:
            print(str(e), file=sys.stderr)
            exit(1)
