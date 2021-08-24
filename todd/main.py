#!/usr/bin/env python3
import sys

from check_req import check_reqs, check_sym_links
from argparse import ArgumentParser


def main() -> int:
    parser = ArgumentParser(description="Run Todd Linux build system")
    parser.add_argument('path', help='path to chroot environment', type=str)
    parser.add_argument('-t','--time', help='measure build time', action='store_true')
    parser.add_argument('-q','--quiet', help='don\'t print messages from underlaying processes', action='store_true')
    parser.add_argument('-j','--jobs', help='number of concurrent jobs (if not specified `nproc` output is used)')
    args = parser.parse_args()


    print("checking requirements: ...")
    all_ok = True
    if not check_reqs():
        all_ok = False
    if not check_sym_links():
        all_ok = False
    if not all_ok:
        print("checking requirements: failure")
        return 1
    print("checking requirements: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
