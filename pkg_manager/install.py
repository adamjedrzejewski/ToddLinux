# See LICENSE for license details.
import sys
import time
import datetime
import json
import os
import shutil
import pathlib
import requests
from typing import List, Dict, Set


FILE_DIR_PATH = pathlib.Path(__file__).parent.resolve()
BUILD_FOLDER = "/tmp/todd_linux_build"


# represents build and installation of <package>
class Package:
    def __init__(self, name: str, src_urls: List[str], env: str, repo: str, build_script: str = None):
        self.name = name
        self.src_urls = src_urls
        self.build_script = f"{repo}/{name}.sh" if build_script is None else f"{repo}/{build_script}"
        self.env = env

    def __repr__(self):
        return f"<Package: '{self.name}' src_urls: {', '.join(self.src_urls)} build_script: '{self.build_script}'>"


def dwn_file(url: str) -> bool:
    local_filename = url.split('/')[-1]
    print(f"downloading {local_filename}: ...")
    with requests.get(url, stream=True) as r:
        if r.status_code != 200:
            print(f"downloading {local_filename}: failure", file=sys.stderr)
            return False
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"downloading {local_filename}: ok")
    return True


def install_package(package: Package, verbose=False) -> bool:
    print(f"preparing {package.name}: ...")
    # delete and create build folder
    if os.path.isdir(BUILD_FOLDER):
        shutil.rmtree(BUILD_FOLDER)
    os.mkdir(BUILD_FOLDER)
    os.chdir("/tmp/todd_linux_build")
    print(f"preparing {package.name}: ok")

    print(f"downloading sources for {package.name}: ...")
    for src in package.src_urls:
        if not dwn_file(src):
            return False

    print(f"running build script for {package.name}: ...")
    cmd_suffix = "" if verbose else " >/dev/null 2>&1"
    if os.system(f"{package.build_script}{cmd_suffix}") != 0:
        print(f"running build script for {package.name}: failure", file=sys.stderr)
        return False

    print(f"running build script for {package.name}: ok")
    return True


# load all available packages from repo
def load_packages(repo: str) -> Dict[str, Package]:
    with open(f"{repo}/packages.json", "r", newline="") as file:
        raw_packages = json.loads(file.read())
    packages = {}
    for raw_pkg in raw_packages["packages"]:
        # check integrity of packages file
        if raw_pkg.get("name") is None or \
                raw_pkg.get("src_urls") is None or \
                raw_pkg.get("env") is None:
            raise ValueError(f"package {raw_pkg} is faulty")

        package = Package(
            raw_pkg["name"],
            raw_pkg["src_urls"],
            raw_pkg["env"],
            repo,
            # using get() <- return None when not found
            raw_pkg.get("build_script"))
        if package.name in packages:
            raise ValueError(f"The repository '{repo}' contains the package '{package.name}' twice")
        packages[package.name] = package

    return packages


def get_installed_packages(lock_file) -> Set[str]:
    installed_packages = set()
    if os.path.isfile(lock_file):
        with open(lock_file, "r", newline="") as file:
            installed_packages = {line.strip() for line in file.readlines()}
    return installed_packages


# install all requested packages in order
def install_packages(names: List[str], repo: str, env: str, lock_file: str, verbose: bool, jobs: int, measure_time: bool) -> bool:
    os.environ["MAKEFLAGS"] = f"-j{jobs}"
    installed_packages = get_installed_packages(lock_file)
    packages = load_packages(repo)

    print("attempting installation of the following packages:")
    print(", ".join(names))
    start = time.time()
    with open(lock_file, "a", newline="") as file:
        for name in names:
            # go/no-go poll for installation
            if name not in packages:
                print(f"package '{name}' couldn't be found")
                return False
            if packages[name].env != env:
                print(f"package '{name}' couldn't be found for environment '{env}'")
                return False
            if name in installed_packages:
                print(f"installing {name}: already installed")
                continue

            if not install_package(packages[name], verbose=verbose):
                return False

            # package has been successfully installed
            file.write(f"{name}\n")
            file.flush()
    end = time.time()
    if measure_time:
        print("all packages installed time:", datetime.timedelta(seconds=(end - start)))
    return True
