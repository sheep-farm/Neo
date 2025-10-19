# Neo - Scrapy Web Scraping Frontend

A modern GTK4/Libadwaita frontend for Scrapy, the powerful web scraping framework.

## Features

- 🕷️ Visual spider creation and management
- ▶️ Live crawl monitoring with start/stop controls
- 📊 Results viewer with JSON/CSV export
- ⚙️ Scrapy settings configuration
- 📱 Responsive adaptive design
- 🎨 Beautiful GNOME integration

## Requirements

- Python 3.10+
- GTK 4
- libadwaita 1.4+
- Scrapy
- PyGObject

## Installation

### From GNOME Builder

1. Clone the repository
2. Open in GNOME Builder
3. Click "Build" button
4. Click "Run" button

### Manual Build
```bash
meson setup build
ninja -C build
ninja -C build install
```

## Usage

1. **Create Spider**: Click + to add a new spider
2. **Configure**: Set URL, selectors, and data fields
3. **Start Crawl**: Click play button to run spider
4. **View Results**: See extracted data in Results tab
5. **Export**: Save results as JSON or CSV

## License

GPL-3.0-or-later

## Author

Your Name <your.email@example.com>
