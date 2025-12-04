"""
Configuration management
"""

import yaml
import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration manager"""

    def __init__(self, config_path: str = "configs/config.yaml"):
        self.config_path = config_path
        self.config_data = {}
        self._load_config()
        self._load_env()

    def _load_config(self):
        """Load configuration from YAML file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config_data = yaml.safe_load(f) or {}
        else:
            print(f"Warning: Config file not found at {self.config_path}")

    def _load_env(self):
        """Load environment variables"""
        load_dotenv()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key (supports dot notation, e.g., 'agents.fraud.threshold')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_env(self, key: str, default: str = None) -> str:
        """
        Get environment variable

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value
        """
        return os.getenv(key, default)

    def get_agent_config(self, agent_name: str) -> Dict:
        """
        Get agent-specific configuration

        Args:
            agent_name: Name of the agent

        Returns:
            Agent configuration dictionary
        """
        return self.get(f'agents.{agent_name}', {})

    def get_api_config(self) -> Dict:
        """Get API configuration"""
        return self.get('api', {})

    def get_database_config(self) -> Dict:
        """Get database configuration"""
        return self.get('database', {})

    def get_logging_config(self) -> Dict:
        """Get logging configuration"""
        return self.get('logging', {})


# Global config instance
_config = None


def get_config(config_path: str = "configs/config.yaml") -> Config:
    """
    Get or create global configuration instance

    Args:
        config_path: Path to configuration file

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config
