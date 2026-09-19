from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import ValidationError

from geodebug.config.model import GeoDebugConfig


class ConfigError(ValueError):
    pass


def find_config(start: Path | None = None) -> Path | None:
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent

    for directory in (current, *current.parents):
        candidate = directory / ".geodebug.toml"
        if candidate.is_file():
            return candidate
    return None


def load_config(
    path: Path | None = None,
    *,
    start: Path | None = None,
) -> GeoDebugConfig:
    config_path = path.resolve() if path is not None else find_config(start)
    if config_path is None:
        return GeoDebugConfig()
    if not config_path.is_file():
        raise ConfigError(f"config file does not exist: {config_path}")

    try:
        with config_path.open("rb") as handle:
            payload = tomllib.load(handle)
        return GeoDebugConfig.model_validate(payload)
    except (OSError, tomllib.TOMLDecodeError, ValidationError) as exc:
        raise ConfigError(f"invalid GeoDebug config: {config_path}: {exc}") from exc
