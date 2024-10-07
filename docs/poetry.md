# Poetry
`socra-python` uses `poetry` for dependency management. Below is a guide on how to use it effectively.

The `pyproject.toml` file contains definitions and dependencies for `socra`, serving a similar purpose to `package.json` in the JavaScript ecosystem.

## Installing Poetry
To contribute to the project, ensure that `poetry` is installed globally on your system. You can follow the instructions [here](https://python-poetry.org/docs/#installing-with-the-official-installer) to install it. Alternatively, you can use the following command for a quick installation:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

## Installing Dependencies
To install the defined dependencies for the project, execute the following command:

```bash
poetry install
```

## Helpful Commands
To activate a virtual shell, use the following command:

```bash
poetry shell
```

To add a new dependency, run:

```bash
poetry add {package name}
```

For running scripts, use the following commands:

```bash
poetry run python your_script.py
poetry run pytest
poetry run black .
```

To update package versions, execute:

```bash
poetry update
``` 

(add any clarification you think is useful)