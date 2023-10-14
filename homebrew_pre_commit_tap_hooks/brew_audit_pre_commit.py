#!/usr/bin/env python3


import argparse
import subprocess
import sys

from path import Path

from homebrew_pre_commit_tap_hooks._version import (
    __version__ as homebrew_pre_commit_tap_hooks_version,
)
from homebrew_pre_commit_tap_hooks.utils import (
    log,
    looks_like_recipe,
    program_name,
    recipe_file_to_names,
)


def real_main(wrapper_args: argparse.Namespace, brew_args: list[str]) -> int:
    print(f"args: {' '.join(sys.argv)}")
    print(f"wrapper_args: {wrapper_args} brew_args: {brew_args}")
    if wrapper_args.version:
        print(f"{program_name} version {homebrew_pre_commit_tap_hooks_version}")
        print(
            subprocess.run(["brew", "--version"], capture_output=True, text=True).stdout,
            end="",
        )
        return 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        if looks_like_recipe(path):
            recipe_names = recipe_file_to_names(path)
            print(f"found formula(s): [{', '.join(recipe_names)}]")
    return 0


def get_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=program_name)
    parser.add_argument(
        "--version", action="store_true", help="Display the version of this program"
    )
    return parser


def main() -> int:
    try:
        arg_parser = get_arg_parser()
        wrapper_args, brew_args = arg_parser.parse_known_intermixed_args()
        return real_main(wrapper_args, brew_args)
    except Exception as e:
        log.exception(f"Received an unexpected exception when running {program_name}")
        return 1
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
