#!/usr/bin/env python3
import sys
import os
import subprocess
import pathlib
from argparse import ArgumentParser
from typing import Optional

from check_req import check_all_reqs
from install_from_host import install_required_packages_from_host

file_dir_path = pathlib.Path(__file__).parent.resolve()
DIRECTORY_LAYOUT = ["bin", "etc", "lib", "lib64", "sbin", "usr", "var", "tools", "builds"]
SIGN_FILE = "lfs_sign.lock"


# create folders in root
def create_directory_layout():
    print("creating minimal directory layout: ...")
    for folder in DIRECTORY_LAYOUT:
        if not os.path.isdir(folder):
            os.mkdir(folder)
    print("creating minimal directory layout: ok")


def main() -> int:
    parser = ArgumentParser(description="Run Todd Linux build system")
    parser.add_argument('path', help='path to chroot environment', type=str)
    parser.add_argument('-t', '--time', help='measure build time', action='store_true')
    parser.add_argument('-v', '--verbose', help='print messages from underlaying build processes', action='store_true')
    parser.add_argument('-j', '--jobs', help='number of concurrent jobs (if not specified `nproc` output is used)')
    args = parser.parse_args()
    verbose: bool = args.verbose
    measure_time: bool = args.time
    jobs: Optional[int] = args.jobs
    lfs_dir = os.path.abspath(args.path)
    os.chdir(lfs_dir)

    # use nproc to determin amount of threads to use
    if jobs is None:
        output = subprocess.check_output("nproc", stderr=subprocess.STDOUT).decode()
        jobs = int(output)

    # "don't fuck up my system"-protection
    if not os.path.exists(SIGN_FILE):
        print(f"Error: provided lfs path '{lfs_dir}' doesn't have sign file; use sign_lfs.py to create one")
        return 1

    if not check_all_reqs():
        return 1

    create_directory_layout()

    if not install_required_packages_from_host(lfs_dir, verbose, jobs, measure_time):
        return 1

    # todo: prepare_chroot missing
    return 0


if __name__ == "__main__":
    sys.exit(main())