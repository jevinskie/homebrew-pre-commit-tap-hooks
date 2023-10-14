#!/usr/bin/env python3


import argparse
import logging
import os
import re
import subprocess
import sys
from typing import Optional

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
    verbose: bool = wrapper_args.verbose_pre_commit
    if verbose:
        log.setLevel(logging.INFO)
        log.info(f"{program_name}: verbose-pre-commit mode enabled")
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


class BrewAuditPreCommitHelpFormatter(argparse.HelpFormatter):
    def __init__(
        self,
        prog: str,
        indent_increment: int = 2,
        max_help_position: int = 24,
        width: int | None = None,
    ) -> None:
        super().__init__(prog, indent_increment, max_help_position, width)

    def format_help(self) -> bytes:
        brew_audit_str = subprocess.run(
            ["brew", "audit", "--help"],
            capture_output=True,
            text=True,
            env={**os.environ, "HOMEBREW_COLOR": "1"},
        ).stdout
        hook_help_lines = brew_audit_str.splitlines()
        hook_help_lines[0] = hook_help_lines[0].replace("audit", "audit-pre-commit")
        hook_help_lines[0] = hook_help_lines[0].replace("...", "Ruby files ...")
        hook_help_lines.insert(
            2,
            "\x1b[1mbrew audit\x1b[0m that still takes Formula/Cask filenames instead of just names.",
        )
        hook_help_lines.insert(3, "")

        for i, line in enumerate(hook_help_lines):
            match: Optional[re.Match] = re.match("^(?P<pre_long_opt>\s+-v, )--verbose\s+", line)
            if match is not None:
                num_chars_before_desc = len(match.group(0))
                pre_commit_verbose_line = (
                    " " * len(match.group("pre_long_opt")) + "--verbose-pre-commit"
                )
                num_spaces_after_verbose_pre_commit = num_chars_before_desc - len(
                    pre_commit_verbose_line
                )
                pre_commit_verbose_line = (
                    pre_commit_verbose_line
                    + " " * num_spaces_after_verbose_pre_commit
                    + f"Make pre-commit hook related output more verbose."
                )
                hook_help_lines.insert(i + 1, pre_commit_verbose_line)
                pre_commit_version_line = " " * len(match.group("pre_long_opt")) + "--version"
                num_spaces_after_pre_commit_version = num_chars_before_desc - len(
                    pre_commit_version_line
                )
                pre_commit_version_line = (
                    pre_commit_version_line
                    + " " * num_spaces_after_pre_commit_version
                    + "Print the version numbers of audit-pre-commit, Homebrew, Homebrew/homebrew-core and Homebrew/homebrew-cask (if tapped) to standard output."
                )
                hook_help_lines.insert(i + 2, pre_commit_version_line)
        hook_help_str = "\n".join(hook_help_lines)
        return hook_help_str + "\n"


def get_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=program_name, formatter_class=BrewAuditPreCommitHelpFormatter
    )
    parser.add_argument(
        "--verbose-pre-commit",
        action="store_true",
        help="Make pre-commit hook related output more verbose.",
    )
    parser.add_argument(
        "--version", action="store_true", help="Display the version of this program."
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
