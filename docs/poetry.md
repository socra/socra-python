# Poetry
`socra-python` uses `poetry` for dependency management. Here's a short guide for how we use it.

`pyproject.toml` includes definitions and dependencies for `socra`. It's similar to `package.json` in JS world.


## Install Poetry
Your system must have `poetry` installed globally in order to contribute.

See [poetry](https://python-poetry.org/docs/#installing-with-the-official-installer) for how to install.

Easiest command:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

## Install dependencies
To install defined dependencies in the project, run
```bash
poetry install
```

## Helpful Commands
Activate a virtual shell
```bash
poetry shell
```

Add a dependency
```bash
poetry add {package name}
```

Running scripts
```bash
poetry run python your_script.py
poetry run pytest
poetry run black .
```

Updating package versions
```bash
poetry update
```