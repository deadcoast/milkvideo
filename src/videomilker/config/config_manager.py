"""Configuration management for VideoMilker."""

import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .settings import Settings
from .defaults import DEFAULT_CONFIG


class ConfigManager:
    """Manages VideoMilker configuration files and settings."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the configuration manager."""
        self.config_dir = config_dir or self._get_default_config_dir()
        self.config_file = self.config_dir / "videomilker.json"
        self.backup_dir = self.config_dir / "backups"
        self.settings: Optional[Settings] = None
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_default_config_dir(self) -> Path:
        """Get the default configuration directory."""
        if Path.home().exists():
            return Path.home() / ".config" / "videomilker"
        return Path.cwd() / "config"
    
    def load_config(self, config_path: Optional[Path] = None) -> Settings:
        """Load configuration from file or create default."""
        config_file = config_path or self.config_file
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle version migration if needed
                data = self._migrate_config(data)
                
                self.settings = Settings(**data)
                return self.settings
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # Backup corrupted config and create new one
                self._backup_corrupted_config(config_file, str(e))
                return self._create_default_config()
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Settings:
        """Create and save default configuration."""
        self.settings = Settings(**DEFAULT_CONFIG)
        self.save_config()
        return self.settings
    
    def save_config(self, config_path: Optional[Path] = None) -> None:
        """Save current configuration to file."""
        if not self.settings:
            raise ValueError("No settings to save")
        
        config_file = config_path or self.config_file
        
        # Create backup before saving
        if config_file.exists():
            self._create_backup(config_file)
        
        # Save new configuration
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings.model_dump(), f, indent=2, default=str)
    
    def _create_backup(self, config_file: Path) -> None:
        """Create a backup of the current configuration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"videomilker_{timestamp}.json"
        shutil.copy2(config_file, backup_file)
    
    def _backup_corrupted_config(self, config_file: Path, error: str) -> None:
        """Backup a corrupted configuration file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"corrupted_{timestamp}.json"
        
        try:
            shutil.copy2(config_file, backup_file)
            # Add error information to backup
            with open(backup_file, 'a', encoding='utf-8') as f:
                f.write(f"\n# Error: {error}\n")
        except Exception:
            pass  # Don't fail if backup fails
    
    def _migrate_config(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate configuration to current version."""
        current_version = "1.0.0"
        config_version = data.get("version", "0.0.0")
        
        if config_version != current_version:
            # Apply migrations based on version
            if config_version < "1.0.0":
                data = self._migrate_to_v1_0_0(data)
            
            data["version"] = current_version
        
        return data
    
    def _migrate_to_v1_0_0(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate configuration to version 1.0.0."""
        # Add any new fields with defaults
        if "download" not in data:
            data["download"] = DEFAULT_CONFIG["download"]
        if "ui" not in data:
            data["ui"] = DEFAULT_CONFIG["ui"]
        if "history" not in data:
            data["history"] = DEFAULT_CONFIG["history"]
        
        return data
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value."""
        if not self.settings:
            self.load_config()
        
        # Support nested keys like "download.path"
        keys = key.split(".")
        value = self.settings
        
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            else:
                return default
        
        return value
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set a specific setting value."""
        if not self.settings:
            self.load_config()
        
        # Support nested keys like "download.path"
        keys = key.split(".")
        obj = self.settings
        
        for k in keys[:-1]:
            if hasattr(obj, k):
                obj = getattr(obj, k)
            else:
                raise KeyError(f"Invalid setting key: {key}")
        
        setattr(obj, keys[-1], value)
    
    def reset_to_defaults(self) -> Settings:
        """Reset configuration to defaults."""
        self.settings = self._create_default_config()
        return self.settings
    
    def export_config(self, export_path: Path) -> None:
        """Export current configuration to a file."""
        if not self.settings:
            self.load_config()
        
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(self.settings.model_dump(), f, indent=2, default=str)
    
    def import_config(self, import_path: Path) -> Settings:
        """Import configuration from a file."""
        if not import_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {import_path}")
        
        with open(import_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate and migrate imported config
        data = self._migrate_config(data)
        self.settings = Settings(**data)
        
        return self.settings 