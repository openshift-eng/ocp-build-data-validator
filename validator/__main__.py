import argparse
import atexit
import sys
from multiprocessing import Pool, cpu_count

from . import format, support, schema, github, distgit, cgit
from . import exceptions, global_session
from validator.schema import releases_schema


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

    releases_cfg = support.load_releases_config_for(file)
    if releases_cfg:
        err = releases_schema.validate(file, releases_cfg)
        if err:
            msg = '\nSchema failure for releases.yml\nReturned error: {}\n\n'.format(err)
            support.fail_validation(msg, parsed)

    if file == 'streams.yml':
        return

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

    (url, err) = cgit.validate(file, parsed, group_cfg)
    if err:
        msg = ('CGit validation failed for {} ({})\n'
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
            pool = Pool(cpu_count(), initializer=global_session.set_global_session)
            atexit.register(pool.close)
            pool.map(validate, args.files)
        except exceptions.ValidationFailedWIP as e:
            print(str(e), file=sys.stderr)
        except (exceptions.ValidationFailed, Exception) as e:
            print(str(e), file=sys.stderr)
            rc = 1

        finally:
            exit(rc)
