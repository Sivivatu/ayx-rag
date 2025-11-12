"""Configuration management for HTML to Markdown conversion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ConversionConfig


DEFAULT_CONFIG = ConversionConfig()


def load_config(config_path: Path | None = None) -> ConversionConfig:
    """
    Load configuration from file or return defaults.

    Args:
        config_path: Optional path to JSON config file

    Returns:
        ConversionConfig instance

    Raises:
        FileNotFoundError: If config_path specified but doesn't exist
        ValueError: If config file is invalid
    """
    if config_path is None:
        return DEFAULT_CONFIG

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}") from e

    return _parse_config(data)


def _parse_config(data: dict[str, Any]) -> ConversionConfig:
    """Parse configuration dictionary into ConversionConfig."""
    config = ConversionConfig()

    # Update thresholds
    if "thresholds" in data:
        thresholds = data["thresholds"]
        if not isinstance(thresholds, dict):
            raise ValueError("thresholds must be a dictionary")
        for key, value in thresholds.items():
            if not isinstance(value, (int, float)):
                raise ValueError(f"Threshold '{key}' must be numeric")
            if not 0 <= value <= 100:
                raise ValueError(f"Threshold '{key}' must be between 0 and 100")
        config.thresholds.update(thresholds)

    # Update exclusions
    if "exclusions" in data:
        exclusions = data["exclusions"]
        if not isinstance(exclusions, list):
            raise ValueError("exclusions must be a list")
        if not all(isinstance(e, str) for e in exclusions):
            raise ValueError("All exclusions must be strings")
        config.exclusions = exclusions

    # Update hybrid_tables
    if "hybrid_tables" in data:
        hybrid_tables = data["hybrid_tables"]
        if not isinstance(hybrid_tables, bool):
            raise ValueError("hybrid_tables must be a boolean")
        config.hybrid_tables = hybrid_tables

    # Update language_map
    if "language_map" in data:
        language_map = data["language_map"]
        if not isinstance(language_map, dict):
            raise ValueError("language_map must be a dictionary")
        if not all(isinstance(k, str) and isinstance(v, str) for k, v in language_map.items()):
            raise ValueError("language_map must have string keys and values")
        config.language_map.update(language_map)

    return config


def save_config(config: ConversionConfig, config_path: Path) -> None:
    """
    Save configuration to JSON file.

    Args:
        config: ConversionConfig instance
        config_path: Path where to save the config
    """
    data = {
        "thresholds": config.thresholds,
        "exclusions": config.exclusions,
        "hybrid_tables": config.hybrid_tables,
        "language_map": config.language_map,
    }

    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
