import argparse
import subprocess
import sys
from .solc_select import (
    valid_install_arg,
    valid_version,
    get_installable_versions,
    install_artifacts,
    switch_global_version,
    current_version,
    installed_versions,
    artifacts_dir,
    halt_old_architecture,
    upgrade_architecture,
)


def solc_select() -> None:
    INSTALL_VERSIONS = "INSTALL_VERSIONS"
    USE_VERSION = "USE_VERSION"
    SHOW_VERSIONS = "SHOW_VERSIONS"
    UPDATE = "UPDATE"

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        help="Allows users to install and quickly switch between Solidity compiler versions"
    )
    parser_install = subparsers.add_parser(
        "install", help="list and install available solc versions"
    )
    parser_install.add_argument(
        INSTALL_VERSIONS,
        help='specific versions you want to install "0.4.25" or "all"',
        nargs="*",
        default=list(),
        type=valid_install_arg,
    )
    parser_use = subparsers.add_parser("use", help="change the version of global solc compiler")
    parser_use.add_argument(
        USE_VERSION, help="solc version you want to use (eg: 0.4.25)", type=valid_version, nargs="?"
    )
    parser_use.add_argument("--always-install", action="store_true")
    parser_use = subparsers.add_parser("versions", help="prints out all installed solc versions")
    parser_use.add_argument(SHOW_VERSIONS, nargs="*", help=argparse.SUPPRESS)
    parser_use = subparsers.add_parser("update", help="upgrades solc-select")
    parser_use.add_argument(UPDATE, nargs="*", help=argparse.SUPPRESS)

    args = vars(parser.parse_args())

    if args.get(INSTALL_VERSIONS) is not None:
        versions = args.get(INSTALL_VERSIONS)
        if versions == []:
            print("Available versions to install:")
            for version in get_installable_versions():
                print(version)
        else:
            install_artifacts(args.get(INSTALL_VERSIONS))

    elif args.get(USE_VERSION) is not None:
        switch_global_version(args.get(USE_VERSION), args.get("always_install"))

    elif args.get(SHOW_VERSIONS) is not None:
        res = current_version()
        if res:
            (current_ver, source) = res
        for version in reversed(sorted(installed_versions())):
            if res and version == current_ver:
                print(f"{version} (current, set by {source})")
            else:
                print(version)
    elif args.get(UPDATE) is not None:
        upgrade_architecture()
    else:
        parser.parse_args(["--help"])
        sys.exit(0)


def solc() -> None:
    res = current_version()
    if res:
        (version, _) = res
        path = artifacts_dir.joinpath(f"solc-{version}", f"solc-{version}")
        halt_old_architecture(path)
        try:
            process = subprocess.run(
                [str(path)] + sys.argv[1:], stdout=subprocess.PIPE, stdin=None, check=True
            )
            print(str(process.stdout, "utf-8"))
        except subprocess.CalledProcessError:
            sys.exit(1)
    else:
        sys.exit(1)
