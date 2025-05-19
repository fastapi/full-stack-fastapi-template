import os
import json
from typing import Dict, Any, Optional, List

class Config:
    """Configuration manager for the UI testing system."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from file or environment variables.
        
        Args:
            config_path: Path to JSON configuration file (optional)
        """
        self.config = {
            # LLM Settings
            "llm_provider": os.environ.get("LLM_PROVIDER", "openai"),  # "openai" or "google"
            "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
            "google_api_key": os.environ.get("GOOGLE_API_KEY", ""),
            "llm_model": os.environ.get("LLM_MODEL", "gpt-4-vision-preview"),
            "temperature": float(os.environ.get("LLM_TEMPERATURE", "0.2")),
            
            # Browser Settings
            "headless": os.environ.get("HEADLESS", "True").lower() == "true",
            "timeout": int(os.environ.get("TIMEOUT", "30000")),  # ms
            "screenshot_on_step": os.environ.get("SCREENSHOT_ON_STEP", "True").lower() == "true",
            
            # Crawling Settings
            "max_pages": int(os.environ.get("MAX_PAGES", "100")),
            "max_depth": int(os.environ.get("MAX_DEPTH", "5")),
            "ignore_external_links": os.environ.get("IGNORE_EXTERNAL", "True").lower() == "true",
            "allowed_domains": [],  # List of allowed domains to crawl
            
            # Authentication
            "auth_required": os.environ.get("AUTH_REQUIRED", "False").lower() == "true",
            "auth_username": os.environ.get("AUTH_USERNAME", ""),
            "auth_password": os.environ.get("AUTH_PASSWORD", ""),
            "auth_type": os.environ.get("AUTH_TYPE", "basic"),  # "basic", "form", or "sso"
            
            # Output Settings
            "output_dir": os.environ.get("OUTPUT_DIR", "outputs"),
            "test_framework": os.environ.get("TEST_FRAMEWORK", "playwright"),  # "playwright" or "selenium"
            "generate_json": os.environ.get("GENERATE_JSON", "True").lower() == "true",
            "generate_test_cases": os.environ.get("GENERATE_TEST_CASES", "True").lower() == "true",
            "generate_code": os.environ.get("GENERATE_CODE", "True").lower() == "true",
            "test_case_format": os.environ.get("TEST_CASE_FORMAT", "gherkin"),  # "gherkin" or "plain"
        }
        
        # Override with file config if provided
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                self.config.update(file_config)
                
        # Create output directories
        self._create_directories()
    
    def _create_directories(self) -> None:
        """Create necessary output directories."""
        os.makedirs(os.path.join(self.config["output_dir"], "metadata"), exist_ok=True)
        os.makedirs(os.path.join(self.config["output_dir"], "test_cases"), exist_ok=True)
        os.makedirs(os.path.join(self.config["output_dir"], "test_scripts", "pages"), exist_ok=True)
        os.makedirs(os.path.join(self.config["output_dir"], "test_scripts", "tests"), exist_ok=True)
        os.makedirs(os.path.join(self.config["output_dir"], "screenshots"), exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Get the entire configuration as a dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()
    
    def save(self, path: str) -> None:
        """Save the configuration to a file.
        
        Args:
            path: Path to save the configuration
        """
        with open(path, 'w') as f:
            json.dump(self.config, f, indent=2)
