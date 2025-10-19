import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw

try:
    from .window import NeoWindow
except ImportError:
    from neo.window import NeoWindow


def main(version):
    """Main entry point"""

    # Criar aplicação Adwaita simples
    app = Adw.Application()

    def on_activate(app):
        """Criar janela quando app ativa"""
        win = NeoWindow(application=app, title="Neo")
        win.present()

    app.connect('activate', on_activate)

    return app.run(sys.argv)
