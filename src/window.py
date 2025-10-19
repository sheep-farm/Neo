from gi.repository import Gtk, Adw, GLib, Gio
import json
import subprocess
import threading
from pathlib import Path
from datetime import datetime

from .spider_dialog import SpiderDialog
from .settings_dialog import ScrapySettingsDialog
from .neo_settings import NeoSettings


class NeoWindow(Adw.ApplicationWindow):
    """Main Neo Window"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new('com.github.youruser.Neo')
        self.neo_settings = NeoSettings()

        # Restore window size
        width = self.settings.get_int('window-width')
        height = self.settings.get_int('window-height')
        self.set_default_size(width, height)

        if self.settings.get_boolean('window-maximized'):
            self.maximize()

        self.set_title("Neo")

        # Scrapy project path
        self.project_path = Path.home() / ".config" / "neo" / "scrapy_project"
        self.ensure_scrapy_project()

        # Estado
        self.spiders = []
        self.active_crawls = {}

        self._build_ui()
        self._load_spiders()

        # Connect signals
        self.connect('close-request', self.on_close_request)

    def on_close_request(self, window):
        """Save window state before closing"""
        self.settings.set_int('window-width', self.get_width())
        self.settings.set_int('window-height', self.get_height())
        self.settings.set_boolean('window-maximized', self.is_maximized())
        return False

    def ensure_scrapy_project(self):
        """Ensure Scrapy project exists"""
        if not self.project_path.exists():
            print("🕷️  Creating Scrapy project...")
            self.project_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                subprocess.run([
                    "scrapy", "startproject", "neo_spiders",
                    str(self.project_path)
                ], check=True)
            except FileNotFoundError:
                print("❌ Scrapy not installed! Please install: pip install scrapy")
            except Exception as e:
                print(f"❌ Error creating Scrapy project: {e}")

    def _build_ui(self):
        """Build main interface"""

        # Header
        self.header = Adw.HeaderBar()

        # New Spider button
        new_spider_btn = Gtk.Button()
        new_spider_btn.set_icon_name("list-add-symbolic")
        new_spider_btn.set_tooltip_text("Create New Spider")
        new_spider_btn.connect("clicked", self.on_new_spider)
        self.header.pack_start(new_spider_btn)

        # Menu
        menu = Gio.Menu()
        menu.append("Settings", "win.settings")
        menu.append("About", "app.about")

        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_menu_model(menu)
        self.header.pack_end(menu_button)

        # Create action for settings
        settings_action = Gio.SimpleAction.new("settings", None)
        settings_action.connect("activate", self.on_settings)
        self.add_action(settings_action)

        # View Switcher Title
        self.view_switcher_title = Adw.ViewSwitcherTitle()
        self.header.set_title_widget(self.view_switcher_title)

        # View Stack
        self.view_stack = Adw.ViewStack()
        self.view_switcher_title.set_stack(self.view_stack)

        # Pages
        spiders_page = self._build_spiders_page()
        self.view_stack.add_titled_with_icon(
            spiders_page, "spiders", "Spiders", "network-server-symbolic"
        )

        crawls_page = self._build_crawls_page()
        self.view_stack.add_titled_with_icon(
            crawls_page, "crawls", "Crawls", "media-playback-start-symbolic"
        )

        results_page = self._build_results_page()
        self.view_stack.add_titled_with_icon(
            results_page, "results", "Results", "folder-documents-symbolic"
        )

        # View Switcher Bar
        self.view_switcher_bar = Adw.ViewSwitcherBar()
        self.view_switcher_bar.set_stack(self.view_stack)

        # Toast Overlay
        self.toast_overlay = Adw.ToastOverlay()

        # Toolbar View
        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(self.header)
        toolbar_view.set_content(self.view_stack)
        toolbar_view.add_bottom_bar(self.view_switcher_bar)

        self.toast_overlay.set_child(toolbar_view)

        # Breakpoint
        breakpoint = Adw.Breakpoint.new(
            Adw.breakpoint_condition_parse("max-width: 550px")
        )
        breakpoint.add_setter(self.view_switcher_bar, "reveal", True)
        breakpoint.add_setter(self.view_switcher_title, "title-visible", False)
        self.add_breakpoint(breakpoint)

        self.set_content(self.toast_overlay)

    def show_toast(self, message, timeout=3):
        """Show toast notification"""
        toast = Adw.Toast.new(message)
        toast.set_timeout(timeout)
        self.toast_overlay.add_toast(toast)

    def _build_spiders_page(self):
        """Build spiders management page"""
        clamp = Adw.Clamp()
        clamp.set_maximum_size(900)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Status
        status_group = Adw.PreferencesGroup()
        status_group.set_margin_top(20)
        status_group.set_margin_start(20)
        status_group.set_margin_end(20)

        self.spiders_status = Adw.ActionRow()
        self.spiders_status.set_title("Configured Spiders")
        self.spiders_status.set_subtitle("0 spiders ready")
        self.spiders_status.set_icon_name("emblem-system-symbolic")
        status_group.add(self.spiders_status)

        box.append(status_group)

        # Spiders list
        spiders_group = Adw.PreferencesGroup()
        spiders_group.set_title("Your Spiders")
        spiders_group.set_description("Scrapy spiders for different websites")
        spiders_group.set_margin_top(10)
        spiders_group.set_margin_start(20)
        spiders_group.set_margin_end(20)
        spiders_group.set_margin_bottom(20)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_min_content_height(400)

        self.spiders_listbox = Gtk.ListBox()
        self.spiders_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.spiders_listbox.add_css_class("boxed-list")

        placeholder = Adw.StatusPage()
        placeholder.set_icon_name("network-server-symbolic")
        placeholder.set_title("No Spiders Yet")
        placeholder.set_description("Create your first spider to start scraping")
        self.spiders_listbox.set_placeholder(placeholder)

        scrolled.set_child(self.spiders_listbox)
        spiders_group.add(scrolled)

        box.append(spiders_group)

        clamp.set_child(box)
        return clamp

    def _build_crawls_page(self):
        """Build active crawls page"""
        clamp = Adw.Clamp()
        clamp.set_maximum_size(900)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        crawls_group = Adw.PreferencesGroup()
        crawls_group.set_title("Active Crawls")
        crawls_group.set_description("Running Scrapy spiders")
        crawls_group.set_margin_top(20)
        crawls_group.set_margin_start(20)
        crawls_group.set_margin_end(20)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_min_content_height(400)

        self.crawls_listbox = Gtk.ListBox()
        self.crawls_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.crawls_listbox.add_css_class("boxed-list")

        placeholder = Adw.StatusPage()
        placeholder.set_icon_name("media-playback-start-symbolic")
        placeholder.set_title("No Active Crawls")
        placeholder.set_description("Start a spider from the Spiders tab")
        self.crawls_listbox.set_placeholder(placeholder)

        scrolled.set_child(self.crawls_listbox)
        crawls_group.add(scrolled)

        box.append(crawls_group)

        clamp.set_child(box)
        return clamp

    def _build_results_page(self):
        """Build results page"""
        clamp = Adw.Clamp()
        clamp.set_maximum_size(1000)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Toolbar
        toolbar_group = Adw.PreferencesGroup()
        toolbar_group.set_margin_top(20)
        toolbar_group.set_margin_start(20)
        toolbar_group.set_margin_end(20)

        filter_row = Adw.ActionRow()
        filter_row.set_title("Results")

        export_btn = Gtk.Button(label="Export")
        export_btn.set_valign(Gtk.Align.CENTER)
        export_btn.connect("clicked", self.on_export_results)
        filter_row.add_suffix(export_btn)

        toolbar_group.add(filter_row)
        box.append(toolbar_group)

        # Results view
        results_group = Adw.PreferencesGroup()
        results_group.set_title("Scraped Items")
        results_group.set_margin_top(10)
        results_group.set_margin_start(20)
        results_group.set_margin_end(20)
        results_group.set_margin_bottom(20)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_min_content_height(400)

        self.results_view = Gtk.TextView()
        self.results_view.set_editable(False)
        self.results_view.set_monospace(True)
        self.results_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.results_view.set_top_margin(12)
        self.results_view.set_bottom_margin(12)
        self.results_view.set_left_margin(12)
        self.results_view.set_right_margin(12)

        buffer = self.results_view.get_buffer()
        buffer.set_text('// No results yet\n// Start a crawl to see items here')

        scrolled.set_child(self.results_view)
        results_group.add(scrolled)

        box.append(results_group)

        clamp.set_child(box)
        return clamp

    def on_new_spider(self, button):
        """Create new spider"""
        dialog = SpiderDialog()
        dialog.connect("spider-created", self.on_spider_created)
        dialog.present()

    def on_spider_created(self, dialog, spider_config):
        """Callback when spider is created"""
        spider_code = self._generate_spider_code(spider_config)

        # Save spider
        spiders_dir = self.project_path / "neo_spiders" / "spiders"
        spiders_dir.mkdir(parents=True, exist_ok=True)

        spider_file = spiders_dir / f"{spider_config['name']}.py"
        spider_file.write_text(spider_code)

        print(f"✅ Spider created: {spider_config['name']}")
        self.show_toast(f"Spider '{spider_config['name']}' created successfully")

        # Save config
        self.neo_settings.save_spider_config(spider_config)

        self._load_spiders()

    def _generate_spider_code(self, config):
        """Generate Scrapy spider Python code"""
        code = f'''import scrapy

class {config['class_name']}(scrapy.Spider):
    name = "{config['name']}"
    allowed_domains = {config['allowed_domains']}
    start_urls = {config['start_urls']}

    custom_settings = {{
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': 'results_{config['name']}.jsonl',
    }}

    def parse(self, response):
        """Extract data using CSS selectors"""
        items = response.css('{config['item_selector']}')

        for item in items:
            yield {{
'''

        for field in config['fields']:
            code += f"                '{field['name']}': item.css('{field['selector']}').get(),\n"

        code += '''            }
'''

        return code

    def _load_spiders(self):
        """Load spiders list from Scrapy project"""
        spiders_dir = self.project_path / "neo_spiders" / "spiders"

        if not spiders_dir.exists():
            return

        self.spiders = []

        for spider_file in spiders_dir.glob("*.py"):
            if spider_file.name == "__init__.py":
                continue

            content = spider_file.read_text()

            import re
            match = re.search(r'name\s*=\s*["\'](.+?)["\']', content)
            if match:
                spider_name = match.group(1)
                self.spiders.append({
                    'name': spider_name,
                    'file': str(spider_file),
                    'class': spider_file.stem
                })

        self._update_spiders_list()

    def _update_spiders_list(self):
        """Update UI with spiders"""
        while child := self.spiders_listbox.get_first_child():
            self.spiders_listbox.remove(child)

        for spider in self.spiders:
            row = self._create_spider_row(spider)
            self.spiders_listbox.append(row)

        count = len(self.spiders)
        self.spiders_status.set_subtitle(f"{count} spider(s) ready")

    def _create_spider_row(self, spider):
        """Create spider row"""
        row = Adw.ActionRow()
        row.set_title(spider['name'])
        row.set_subtitle(f"Class: {spider['class']}")
        row.set_icon_name("applications-science-symbolic")

        # Start button
        start_btn = Gtk.Button()
        start_btn.set_icon_name("media-playback-start-symbolic")
        start_btn.set_valign(Gtk.Align.CENTER)
        start_btn.set_tooltip_text("Start crawl")
        start_btn.add_css_class("suggested-action")
        start_btn.add_css_class("circular")
        start_btn.connect("clicked", self.on_start_crawl, spider)
        row.add_suffix(start_btn)

        return row

    def on_start_crawl(self, button, spider):
        """Start spider crawl"""
        print(f"🕷️  Starting crawl: {spider['name']}")
        self.show_toast(f"Starting {spider['name']}...")

        def run_spider():
            try:
                process = subprocess.Popen(
                    ["scrapy", "crawl", spider['name']],
                    cwd=str(self.project_path / "neo_spiders"),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                self.active_crawls[spider['name']] = process

                GLib.idle_add(self._add_crawl_to_ui, spider)

                stdout, stderr = process.communicate()

                print(f"✅ Crawl finished: {spider['name']}")
                if stdout:
                    print(stdout)
                if stderr:
                    print("Errors:", stderr)

                if spider['name'] in self.active_crawls:
                    del self.active_crawls[spider['name']]

                GLib.idle_add(self._remove_crawl_from_ui, spider)
                GLib.idle_add(self._load_results, spider)
                GLib.idle_add(self.show_toast, f"Crawl '{spider['name']}' finished")

            except Exception as e:
                print(f"❌ Error running spider: {e}")
                GLib.idle_add(self.show_toast, f"Error: {e}")

        thread = threading.Thread(target=run_spider, daemon=True)
        thread.start()

    def _add_crawl_to_ui(self, spider):
        """Add active crawl to UI"""
        row = Adw.ActionRow()
        row.set_title(spider['name'])
        row.set_subtitle("Crawling...")

        spinner = Gtk.Spinner()
        spinner.set_spinning(True)
        spinner.set_valign(Gtk.Align.CENTER)
        row.add_suffix(spinner)

        stop_btn = Gtk.Button()
        stop_btn.set_icon_name("media-playback-stop-symbolic")
        stop_btn.set_valign(Gtk.Align.CENTER)
        stop_btn.add_css_class("destructive-action")
        stop_btn.add_css_class("circular")
        stop_btn.connect("clicked", self.on_stop_crawl, spider)
        row.add_suffix(stop_btn)

        row.set_name(f"crawl_{spider['name']}")
        self.crawls_listbox.append(row)

        self.view_stack.set_visible_child_name("crawls")

    def _remove_crawl_from_ui(self, spider):
        """Remove crawl from UI"""
        child = self.crawls_listbox.get_first_child()
        while child:
            if child.get_name() == f"crawl_{spider['name']}":
                self.crawls_listbox.remove(child)
                break
            child = child.get_next_sibling()

    def on_stop_crawl(self, button, spider):
        """Stop active crawl"""
        if spider['name'] in self.active_crawls:
            process = self.active_crawls[spider['name']]
            process.terminate()
            print(f"🛑 Stopped: {spider['name']}")
            self.show_toast(f"Stopped {spider['name']}")

    def _load_results(self, spider):
        """Load spider results"""
        results_file = self.project_path / "neo_spiders" / f"results_{spider['name']}.jsonl"

        if not results_file.exists():
            return

        items = []
        with open(results_file, 'r') as f:
            for line in f:
                try:
                    items.append(json.loads(line))
                except:
                    pass

        buffer = self.results_view.get_buffer()
        results_text = json.dumps(items, indent=2, ensure_ascii=False)
        buffer.set_text(results_text)

        print(f"📦 Loaded {len(items)} items from {spider['name']}")

        self.view_stack.set_visible_child_name("results")

    def on_settings(self, action, param):
        """Open Scrapy settings dialog"""
        dialog = ScrapySettingsDialog()
        dialog.present()

    def on_export_results(self, button):
        """Export results to file"""
        buffer = self.results_view.get_buffer()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        results_text = buffer.get_text(start, end, False)

        if not results_text or results_text.startswith('// No results'):
            self.show_toast("No results to export")
            return

        dialog = Gtk.FileDialog()
        dialog.set_title("Export Results")
        dialog.set_initial_name("results.json")

        filters = Gio.ListStore.new(Gtk.FileFilter)

        json_filter = Gtk.FileFilter()
        json_filter.set_name("JSON files")
        json_filter.add_pattern("*.json")
        filters.append(json_filter)

        csv_filter = Gtk.FileFilter()
        csv_filter.set_name("CSV files")
        csv_filter.add_pattern("*.csv")
        filters.append(csv_filter)

        dialog.set_filters(filters)
        dialog.save(self, None, self.on_export_response, results_text)

    def on_export_response(self, dialog, result, results_text):
        """Callback for export file chooser"""
        try:
            file = dialog.save_finish(result)
            if file:
                filepath = file.get_path()

                if filepath.endswith('.json'):
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(results_text)

                elif filepath.endswith('.csv'):
                    import csv
                    items = json.loads(results_text)

                    if items:
                        keys = items[0].keys()
                        with open(filepath, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.DictWriter(f, fieldnames=keys)
                            writer.writeheader()
                            writer.writerows(items)

                print(f"💾 Exported to: {filepath}")
                self.show_toast("Results exported successfully")

        except Exception as e:
            print(f"❌ Export error: {e}")
            self.show_toast(f"Export failed: {e}")                    
