#!/usr/bin/env python3

#:  * `audit-pre-commit` [<options>]
#:
#:  `brew audit` that still takes Formula/Cask filenames instead of just names
#:
#:          --merge                      Use `git merge` to apply updates (rather than `git rebase`).
#:          --preinstall                 Run on auto-updates (e.g. before `brew install`). Skips some slower steps.
#:      -f, --force                      Always do a slower, full update check (even if unnecessary).
#:      -v, --verbose                    Print the directories checked and `git` operations performed.
#:      -d, --debug                      Display a trace of all shell commands as they are executed.
#:      -h, --help                       Show this message.

import argparse
import subprocess
import sys

from path import Path

from pre_commit_homebrew_tap._version import (
    __version__ as pre_commit_homebrew_tap_version,
)
from pre_commit_homebrew_tap.utils import (
    log,
    looks_like_recipe,
    program_name,
    recipe_file_to_names,
)


def real_main(wrapper_args: argparse.Namespace, brew_args: list[str]) -> int:
    print(f"args: {' '.join(sys.argv)}")
    print(f"wrapper_args: {wrapper_args} brew_args: {brew_args}")
    if wrapper_args.version:
        print(f"{program_name} version {pre_commit_homebrew_tap_version}")
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
