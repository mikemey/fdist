import sys


def run_tests(args=None):
    import pytest

    if not args:
        args = []

    if not any(a for a in args[1:] if not a.startswith('-')):
        args.append('test')
        args.append('fdist')

    sys.exit(pytest.main(args))


if __name__ == '__main__':
    run_tests(sys.argv)
