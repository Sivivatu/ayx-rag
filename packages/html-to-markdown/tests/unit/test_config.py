"""Unit tests for configuration management."""

import json
from pathlib import Path

import pytest
from html_to_markdown.config import DEFAULT_CONFIG, load_config, save_config
from html_to_markdown.models import ConversionConfig


class TestLoadConfig:
    """Tests for configuration loading."""

    def test_load_config_default_when_none(self):
        """Test loading default config when no path specified."""
        config = load_config(None)

        assert config.thresholds["heading_fidelity"] == 90.0
        assert config.hybrid_tables is True
        assert len(config.exclusions) > 0

    def test_load_config_file_not_found(self, tmp_path: Path):
        """Test error when config file doesn't exist."""
        config_path = tmp_path / "missing.json"

        with pytest.raises(FileNotFoundError, match="Config file not found"):
            load_config(config_path)

    def test_load_config_invalid_json(self, tmp_path: Path):
        """Test error when config file has invalid JSON."""
        config_path = tmp_path / "invalid.json"
        config_path.write_text("{invalid json")

        with pytest.raises(ValueError, match="Invalid JSON"):
            load_config(config_path)

    def test_load_config_valid_file(self, tmp_path: Path):
        """Test loading valid config file."""
        config_path = tmp_path / "config.json"
        config_data = {
            "thresholds": {"heading_fidelity": 85.0, "link_preservation": 90.0},
            "exclusions": ["**/build/**"],
            "hybrid_tables": False,
            "language_map": {"test-lang": "test"},
        }
        config_path.write_text(json.dumps(config_data))

        config = load_config(config_path)

        assert config.thresholds["heading_fidelity"] == 85.0
        assert config.thresholds["link_preservation"] == 90.0
        assert config.exclusions == ["**/build/**"]
        assert config.hybrid_tables is False
        assert config.language_map["test-lang"] == "test"

    def test_load_config_partial_overrides(self, tmp_path: Path):
        """Test loading config with partial overrides."""
        config_path = tmp_path / "config.json"
        config_data = {"thresholds": {"heading_fidelity": 75.0}}
        config_path.write_text(json.dumps(config_data))

        config = load_config(config_path)

        # Override applied
        assert config.thresholds["heading_fidelity"] == 75.0
        # Defaults preserved
        assert config.thresholds["link_preservation"] == 95.0
        assert config.hybrid_tables is True

    def test_load_config_invalid_threshold_type(self, tmp_path: Path):
        """Test error when threshold value is not numeric."""
        config_path = tmp_path / "config.json"
        config_data = {"thresholds": {"heading_fidelity": "not a number"}}
        config_path.write_text(json.dumps(config_data))

        with pytest.raises(ValueError, match="must be numeric"):
            load_config(config_path)

    def test_load_config_threshold_out_of_range(self, tmp_path: Path):
        """Test error when threshold value is out of range."""
        config_path = tmp_path / "config.json"
        config_data = {"thresholds": {"heading_fidelity": 150.0}}
        config_path.write_text(json.dumps(config_data))

        with pytest.raises(ValueError, match="must be between 0 and 100"):
            load_config(config_path)

    def test_load_config_invalid_exclusions_type(self, tmp_path: Path):
        """Test error when exclusions is not a list."""
        config_path = tmp_path / "config.json"
        config_data = {"exclusions": "not a list"}
        config_path.write_text(json.dumps(config_data))

        with pytest.raises(ValueError, match="exclusions must be a list"):
            load_config(config_path)

    def test_load_config_invalid_hybrid_tables_type(self, tmp_path: Path):
        """Test error when hybrid_tables is not a boolean."""
        config_path = tmp_path / "config.json"
        config_data = {"hybrid_tables": "not a boolean"}
        config_path.write_text(json.dumps(config_data))

        with pytest.raises(ValueError, match="hybrid_tables must be a boolean"):
            load_config(config_path)


class TestSaveConfig:
    """Tests for configuration saving."""

    def test_save_config_creates_file(self, tmp_path: Path):
        """Test saving config creates JSON file."""
        config = ConversionConfig(
            thresholds={"test_threshold": 80.0},
            exclusions=["**/test/**"],
            hybrid_tables=False,
            language_map={"test": "test"},
        )
        config_path = tmp_path / "config.json"

        save_config(config, config_path)

        assert config_path.exists()
        data = json.loads(config_path.read_text())
        assert data["thresholds"]["test_threshold"] == 80.0
        assert data["exclusions"] == ["**/test/**"]
        assert data["hybrid_tables"] is False
        assert data["language_map"]["test"] == "test"

    def test_save_config_creates_parent_dir(self, tmp_path: Path):
        """Test saving config creates parent directories."""
        config = ConversionConfig()
        config_path = tmp_path / "nested" / "dir" / "config.json"

        save_config(config, config_path)

        assert config_path.exists()
        assert config_path.parent.exists()


class TestDefaultConfig:
    """Tests for default configuration."""

    def test_default_config_exists(self):
        """Test DEFAULT_CONFIG is properly initialized."""
        assert DEFAULT_CONFIG is not None
        assert isinstance(DEFAULT_CONFIG, ConversionConfig)
        assert len(DEFAULT_CONFIG.thresholds) > 0
        assert len(DEFAULT_CONFIG.language_map) > 0
