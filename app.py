import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Gio, GLib, GObject, GdkPixbuf


if __name__ == "__main__":
    from main_window import MyWindow

    win = MyWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
