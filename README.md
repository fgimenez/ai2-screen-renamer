# ai2-screen-renamer

A command-line tool to rename screens in [MIT App Inventor 2](https://appinventor.mit.edu/) projects (`.aia` files).

App Inventor does not provide a built-in way to rename screens. This tool automates the process by editing the `.aia` file directly, updating all internal references consistently.

## What it does

For a given screen rename (`OldName` → `NewName`), the tool updates:

- `OldName.scm` → `NewName.scm` (Designer components file)
- `OldName.bky` → `NewName.bky` (Blocks file)
- `$Name` field inside the `.scm` file
- `main=` and `lastopened=` entries in `youngandroidproject/project.properties`
- Any `open another screen` block references in other screens' `.bky` files

## Installation

Requires Python 3.10+.

```bash
pip install ai2-screen-renamer
```

Or install from source:

```bash
git clone https://github.com/fgimenez/ai2-screen-renamer.git
cd ai2-screen-renamer
pip install -e .
```

## Usage

```bash
# Rename Screen1 to AgendaContactos, output to MyApp_AgendaContactos.aia
ai2-screen-renamer MyApp.aia Screen1 AgendaContactos

# Specify output file explicitly
ai2-screen-renamer MyApp.aia Screen1 AgendaContactos MyApp_renamed.aia
```

Or as a Python module:

```bash
python -m ai2_renamer MyApp.aia Screen1 AgendaContactos
```

## Errors

The tool raises a descriptive error if:

- The input file is not a valid `.aia` file
- The screen to rename does not exist in the project
- A screen with the new name already exists in the project

## Development

```bash
pip install -e ".[dev]"
pytest -v
```

## License

Apache 2.0
