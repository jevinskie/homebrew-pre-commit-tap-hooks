import logging
import sys

from path import Path
from rich.console import Console
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.WARNING,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=Console(stderr=True))],
)


def get_pretty_program_name() -> str:
    raw_path = Path(sys.argv[0])
    subcmd = raw_path.name.removeprefix("brew-")
    return f"brew {subcmd}"


program_name = get_pretty_program_name()

log = logging.getLogger(program_name)
