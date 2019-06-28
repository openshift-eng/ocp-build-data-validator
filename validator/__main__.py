from __future__ import print_function
from multiprocessing import Pool, cpu_count
import argparse
import sys

from . import format, support, schema, github, distgit


def validate(file):
    print('Validating {}'.format(file))

    (parsed, err) = format.validate(open(file).read())
    if err:
        raise Exception(('{} is not a valid YAML\n'
                         'Returned error: {}').format(file, err))

    err = schema.validate(file, parsed)
    if err:
        raise Exception(('schema mismatch: {}\n'
                         'Returned error: {}').format(file, err))

    group_cfg = support.load_group_config_for(file)

    (url, err) = github.validate(parsed, group_cfg)
    if err:
        raise Exception(('GitHub validation failed for {}\n'
                         'Returned error: {}').format(url, err))

    (url, err) = distgit.validate(file, parsed, group_cfg)
    if err:
        raise Exception(('DistGit validation failed for {}\n'
                         'Returned error: {}').format(url, err))


def main():
    parser = argparse.ArgumentParser(
        description='Validation of ocp-build-data Image & RPM declarations')
    parser.add_argument('files',
                        metavar='FILE',
                        type=str,
                        nargs='+',
                        help='Files to be validated')
    args = parser.parse_args()

    try:
        Pool(cpu_count()).map(validate, args.files)
    except Exception as e:
        print(str(e), file=sys.stderr)
        exit(1)
