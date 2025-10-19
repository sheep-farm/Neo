import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio

try:
    from .window import NeoWindow
except ImportError:
    from neo.window import NeoWindow


class NeoApplication(Adw.Application):
    """Main Neo Application class"""

    def __init__(self, version):
        # Usar NON_UNIQUE para não registrar no D-Bus
        super().__init__(
            application_id='com.github.youruser.Neo',
            flags=Gio.ApplicationFlags.NON_UNIQUE
        )
        self.version = version

    def do_activate(self):
        """Called when the application is activated"""
        win = self.props.active_window
        if not win:
            win = NeoWindow(application=self)
        win.present()

    def do_startup(self):
        """Application startup"""
        Adw.Application.do_startup(self)

        # Criar actions
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)

    def on_about_action(self, widget, _):
        """Callback for the app.about action"""
        about = Adw.AboutWindow(
            transient_for=self.props.active_window,
            application_name='Neo',
            application_icon='com.github.youruser.Neo',
            developer_name='Your Name',
            version=self.version,
            developers=['Your Name'],
            copyright='© 2025 Your Name',
            license_type=Gtk.License.GPL_3_0,
        )
        about.present()

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action"""
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """Main entry point"""
    app = NeoApplication(version)
    return app.run(sys.argv)
