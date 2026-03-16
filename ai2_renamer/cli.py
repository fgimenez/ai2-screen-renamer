import sys
from pathlib import Path
from ai2_renamer import rename_screen


def main(args: list[str] | None = None) -> None:
    if args is None:
        args = sys.argv[1:]
    input_path, old_name, new_name, *rest = args
    output_path = rest[0] if rest else _auto_output(input_path, new_name)
    data = Path(input_path).read_bytes()
    result = rename_screen(data, old_name, new_name)
    Path(output_path).write_bytes(result)


def _auto_output(input_path: str, new_name: str) -> str:
    p = Path(input_path)
    return str(p.with_name(f"{p.stem}_{new_name}{p.suffix}"))
