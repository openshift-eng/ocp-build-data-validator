from __future__ import print_function

import argparse
import sys
import re
from multiprocessing import Pool, cpu_count

from . import format, support, schema, github, distgit
from . import exceptions, global_session


class NoRelaseSet(object):
    def __init__(self):
        self.data = set()

    def cached(self, group_cfg, btype):
        if self.data:
            return self.data
        else:
            self.data = set(group_cfg['non_release'][btype])
            return self.data


non_release_set = NoRelaseSet()


def skip_non_release(file, group_cfg, btype):
    try:
        res = re.split('.yml|.yaml', file)[0].rsplit('/', 1)
        build_name = res[0] if len(res) == 1 else res[1]
        if build_name in non_release_set.cached(group_cfg, btype):
            print('Skipping validation of non_release {} {}.'.format(btype, file))
            return True
        else:
            return False
    except IndexError as error:
        raise exceptions.ValidationFailedSkipNonRelease(error)


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

    if skip_non_release(file, group_cfg, 'images'):
        return

    if skip_non_release(file, group_cfg, 'rpms'):
        return

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
            rc = 0
            Pool(cpu_count(),
                 initializer=global_session.set_global_session).map(
                 validate, args.files)
        except exceptions.ValidationFailedWIP as e:
            print(str(e), file=sys.stderr)

        except (exceptions.ValidationFailed, Exception) as e:
            print(str(e), file=sys.stderr)
            rc += 1

        finally:
            exit(rc)
