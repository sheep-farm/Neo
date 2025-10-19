# settings.py
import json
from pathlib import Path
from gi.repository import Gio

class NeoSettings:
    """Gerencia configurações do Neo"""

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "neo"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.spiders_file = self.config_dir / "spiders.json"
        self.settings_file = self.config_dir / "scrapy_settings.json"

    def save_spider_config(self, spider_config):
        """Salva configuração de spider"""
        spiders = self.load_spiders_config()
        spiders.append(spider_config)

        with open(self.spiders_file, 'w') as f:
            json.dump(spiders, f, indent=2)

    def load_spiders_config(self):
        """Carrega configurações de spiders"""
        if not self.spiders_file.exists():
            return []

        with open(self.spiders_file, 'r') as f:
            return json.load(f)

    def save_scrapy_settings(self, settings):
        """Salva settings do Scrapy"""
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=2)

    def load_scrapy_settings(self):
        """Carrega settings do Scrapy"""
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

        with open(self.settings_file, 'r') as f:
            return json.load(f)
