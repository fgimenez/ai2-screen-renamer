import argparse
import sys
from pathlib import Path
from ai2_renamer import rename_screen

USAGE = "usage: ai2-screen-renamer INPUT.aia OLD_NAME NEW_NAME [OUTPUT.aia]"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai2-screen-renamer",
        description="Rename a screen in an MIT App Inventor 2 (.aia) project.",
        usage="%(prog)s INPUT.aia OLD_NAME NEW_NAME [OUTPUT.aia]",
    )
    parser.add_argument("input", metavar="INPUT.aia")
    parser.add_argument("old_name", metavar="OLD_NAME")
    parser.add_argument("new_name", metavar="NEW_NAME")
    parser.add_argument("output", metavar="OUTPUT.aia", nargs="?")
    return parser


def main(args: list[str] | None = None) -> None:
    parser = _build_parser()
    parsed = parser.parse_args(args)
    output_path = parsed.output or _auto_output(parsed.input, parsed.new_name)
    try:
        data = Path(parsed.input).read_bytes()
        result = rename_screen(data, parsed.old_name, parsed.new_name)
        Path(output_path).write_bytes(result)
    except (ValueError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


def _auto_output(input_path: str, new_name: str) -> str:
    p = Path(input_path)
    return str(p.with_name(f"{p.stem}_{new_name}{p.suffix}"))
