import json
from pathlib import Path


class NeoSettings:
    """Manage Neo application settings"""

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "neo"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.spiders_file = self.config_dir / "spiders.json"
        self.settings_file = self.config_dir / "scrapy_settings.json"

    def save_spider_config(self, spider_config):
        """Save spider configuration"""
        spiders = self.load_spiders_config()
        spiders.append(spider_config)

        with open(self.spiders_file, 'w') as f:
            json.dump(spiders, f, indent=2)

    def load_spiders_config(self):
        """Load spider configurations"""
        if not self.spiders_file.exists():
            return []

        try:
            with open(self.spiders_file, 'r') as f:
                return json.load(f)
        except:
            return []

    def save_scrapy_settings(self, settings):
        """Save Scrapy settings"""
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=2)

    def load_scrapy_settings(self):
        """Load Scrapy settings"""
        default_settings = {
            'CONCURRENT_REQUESTS': 16,
            'DOWNLOAD_DELAY': 0,
            'ROBOTSTXT_OBEY': True,
            'USER_AGENT': 'Neo/1.0 (+https://github.com/user/neo)',
            'AUTOTHROTTLE_ENABLED': True,
            'HTTPCACHE_ENABLED': True,
        }

        if not self.settings_file.exists():
            return default_settings

        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except:
            return default_settings
