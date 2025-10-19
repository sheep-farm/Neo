from gi.repository import Gtk, Adw, GLib, GObject


class FieldDialog(Adw.Dialog):
    """Dialog for adding field to spider"""

    __gsignals__ = {
        'field-added': (GObject.SignalFlags.RUN_FIRST, None, (object,))
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("Add Field")
        self.set_content_width(450)
        self.set_content_height(300)

        self._build_ui()

    def _build_ui(self):
        """Build field dialog UI"""
        content = Adw.ToolbarView()

        header = Adw.HeaderBar()
        header.set_show_title(False)

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda b: self.close())
        header.pack_start(cancel_btn)

        add_btn = Gtk.Button(label="Add")
        add_btn.add_css_class("suggested-action")
        add_btn.connect("clicked", self.on_add_clicked)
        header.pack_end(add_btn)

        content.add_top_bar(header)

        # Form
        form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        group = Adw.PreferencesGroup()
        group.set_margin_top(20)
        group.set_margin_start(20)
        group.set_margin_end(20)

        self.field_name_row = Adw.EntryRow()
        self.field_name_row.set_title("Field Name")
        self.field_name_row.get_delegate().set_placeholder_text("title, price, url...")
        group.add(self.field_name_row)

        self.field_selector_row = Adw.EntryRow()
        self.field_selector_row.set_title("CSS Selector")
        self.field_selector_row.get_delegate().set_placeholder_text("h1.title::text")
        group.add(self.field_selector_row)

        form_box.append(group)

        content.set_content(form_box)
        self.set_child(content)

    def on_add_clicked(self, button):
        """Add field"""
        field_data = {
            'name': self.field_name_row.get_text(),
            'selector': self.field_selector_row.get_text()
        }

        if field_data['name'] and field_data['selector']:
            self.emit('field-added', field_data)
            self.close()
