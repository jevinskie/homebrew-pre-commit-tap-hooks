import json
import os
import subprocess
import sys

from path import Path
from rich import print

from homebrew_pre_commit_tap_hooks.log import log, program_name


def looks_like_recipe(path: Path) -> tuple[bool, bool]:
    if path.isfile() and path.ext == ".rb":
        parent_dir = path.parts()[-2]
        is_cask = False
        if parent_dir == "Formula":
            pass
        elif parent_dir == "Casks":
            is_cask = True
        else:
            return (False, False)
        if not path.access(os.R_OK):
            raise PermissionError(f"Can't read {'Cask' if is_cask else 'Formula'} '{path}'")
        return (True, is_cask)
    return (False, False)


def recipe_file_to_names(recipe_file: Path) -> list[tuple[str, bool]]:
    names: list[tuple[str, bool]] = []
    is_recipe, is_cask = looks_like_recipe(recipe_file)
    if not is_recipe:
        return names
    brew_info_cmd = (
        "brew",
        "info",
        "--json=v2",
        "--formula",
        "--cask" if is_cask else "--formula",
        recipe_file,
    )
    log.info(f"{program_name} is running '{' '.join(brew_info_cmd)}'")
    try:
        info_res = subprocess.run(
            brew_info_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        log.error(f"brew info output:\n{e.output}")
        log.exception(
            f"{program_name} got return code {e.returncode} while running '{' '.join(brew_info_cmd)}'"
        )
        sys.exit(e.returncode)
    except Exception as e:
        log.error(f"brew info output:\n{info_res.stdout}")
        log.exception(f"Received an unexpected exception when running '{' '.join(brew_info_cmd)}'")
        sys.exit(1)
    info = json.loads(info_res.stdout)
    for formula in info["formulae"]:
        names.append((formula["name"], False))
    for cask in info["casks"]:
        names.append((cask["name"], True))
    return names
