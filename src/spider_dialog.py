from gi.repository import Gtk, Adw, GLib, GObject
from datetime import datetime

from .field_dialog import FieldDialog

class SpiderDialog(Adw.Dialog):
    """Dialog for creating new spider"""

    __gsignals__ = {
        'spider-created': (GObject.SignalFlags.RUN_FIRST, None, (object,))
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("New Spider")
        self.set_content_width(600)
        self.set_content_height(550)

        self.fields = []

        self._build_ui()

    def _build_ui(self):
        """Build dialog interface"""
        content = Adw.ToolbarView()

        # Header
        header = Adw.HeaderBar()
        header.set_show_title(False)

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda b: self.close())
        header.pack_start(cancel_btn)

        create_btn = Gtk.Button(label="Create")
        create_btn.add_css_class("suggested-action")
        create_btn.connect("clicked", self.on_create_clicked)
        header.pack_end(create_btn)

        content.add_top_bar(header)

        # Form
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Basic info
        basic_group = Adw.PreferencesGroup()
        basic_group.set_title("Spider Configuration")
        basic_group.set_margin_top(20)
        basic_group.set_margin_start(20)
        basic_group.set_margin_end(20)

        self.name_row = Adw.EntryRow()
        self.name_row.set_title("Spider Name")
        self.name_row.get_delegate().set_placeholder_text("my_spider")
        basic_group.add(self.name_row)

        self.start_url_row = Adw.EntryRow()
        self.start_url_row.set_title("Start URL")
        self.start_url_row.get_delegate().set_placeholder_text("https://example.com")
        basic_group.add(self.start_url_row)

        self.domain_row = Adw.EntryRow()
        self.domain_row.set_title("Allowed Domain")
        self.domain_row.get_delegate().set_placeholder_text("example.com")
        basic_group.add(self.domain_row)

        self.selector_row = Adw.EntryRow()
        self.selector_row.set_title("Item Selector (CSS)")
        self.selector_row.get_delegate().set_placeholder_text("div.item, article")
        basic_group.add(self.selector_row)

        form_box.append(basic_group)

        # Fields
        fields_group = Adw.PreferencesGroup()
        fields_group.set_title("Data Fields")
        fields_group.set_description("Define what data to extract")
        fields_group.set_margin_top(10)
        fields_group.set_margin_start(20)
        fields_group.set_margin_end(20)
        fields_group.set_margin_bottom(20)

        # Add field button
        add_field_row = Adw.ActionRow()
        add_field_row.set_title("Add Field")

        add_btn = Gtk.Button()
        add_btn.set_icon_name("list-add-symbolic")
        add_btn.set_valign(Gtk.Align.CENTER)
        add_btn.add_css_class("flat")
        add_btn.connect("clicked", self.on_add_field)
        add_field_row.add_suffix(add_btn)

        fields_group.add(add_field_row)

        # Fields listbox
        self.fields_listbox = Gtk.ListBox()
        self.fields_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.fields_listbox.add_css_class("boxed-list")
        fields_group.add(self.fields_listbox)

        form_box.append(fields_group)

        scrolled.set_child(form_box)
        content.set_content(scrolled)

        self.set_child(content)

    def on_add_field(self, button):
        """Add new field"""
        dialog = FieldDialog(transient_for=self.get_root())
        dialog.connect("field-added", self.on_field_added)
        dialog.present()

    def on_field_added(self, dialog, field_data):
        """Callback when field is added"""
        self.fields.append(field_data)

        row = Adw.ActionRow()
        row.set_title(field_data['name'])
        row.set_subtitle(field_data['selector'])

        remove_btn = Gtk.Button()
        remove_btn.set_icon_name("user-trash-symbolic")
        remove_btn.set_valign(Gtk.Align.CENTER)
        remove_btn.add_css_class("flat")
        remove_btn.add_css_class("circular")
        remove_btn.connect("clicked", lambda b: self.on_remove_field(row, field_data))
        row.add_suffix(remove_btn)

        self.fields_listbox.append(row)

    def on_remove_field(self, row, field_data):
        """Remove field"""
        self.fields.remove(field_data)
        self.fields_listbox.remove(row)

    def on_create_clicked(self, button):
        """Create spider"""
        name = self.name_row.get_text()
        start_url = self.start_url_row.get_text()
        domain = self.domain_row.get_text()
        item_selector = self.selector_row.get_text()

        if not all([name, start_url, domain, item_selector]):
            print("❌ Fill all fields")
            return

        class_name = ''.join(word.capitalize() for word in name.split('_'))

        spider_config = {
            'name': name,
            'class_name': class_name + 'Spider',
            'start_urls': [start_url],
            'allowed_domains': [domain],
            'item_selector': item_selector,
            'fields': self.fields,
            'created': datetime.now().isoformat()
        }

        self.emit('spider-created', spider_config)
        self.close()
