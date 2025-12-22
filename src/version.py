"""Version helper module for reading version from pyproject.toml."""

import tomllib
from pathlib import Path


def get_version() -> str:
    """
    Read and return the version string from pyproject.toml.

    Returns:
        str: The version string from the [project] section of pyproject.toml

    Raises:
        FileNotFoundError: If pyproject.toml cannot be found
        KeyError: If version field is not present in pyproject.toml
    """
    # Get the project root directory (parent of src)
    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / "pyproject.toml"

    # Read and parse pyproject.toml
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)

    # Extract version from [project] section
    return pyproject_data["project"]["version"]
