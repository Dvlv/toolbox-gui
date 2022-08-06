import os
from app import Gtk, GdkPixbuf
from utils import set_icon_at_small_size


class AboutWindow(Gtk.MessageDialog):
    def __init__(self, parent):
        super().__init__(title=f"About", transient_for=parent, flags=0)

        self.add_buttons(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

        main_box = self.get_content_area()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.set_border_width(20)

        program_icon = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "icons", "co.uk.dvlv.toolbox-gui.svg"))

        img = Gtk.Image()
        pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(program_icon, 64, 64, True)
        img.set_from_pixbuf(pb)

        vbox.add(img)

        markup = """
        A graphical manager for your toolboxes
        Released under the MIT Licence
        """
        for line in markup.split("\n"):
            lbl = Gtk.Label(label=line)
            vbox.add(lbl)


        self.format_secondary_text("Toolbox GUI")

        main_box.add(vbox)

        self.show_all()