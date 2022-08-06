from app import Gtk
from utils import set_icon_at_small_size


class HelpWindow(Gtk.MessageDialog):
    def __init__(self, parent):
        super().__init__(title=f"Help", transient_for=parent, flags=0)

        self.add_buttons(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

        box = self.get_content_area()

        spacer = Gtk.Box(spacing=10)
        spacer.set_border_width(20)

        grid = Gtk.Grid()
        grid.set_column_spacing(20)
        grid.set_row_spacing(20)

        help_parts = {
            "list-add-symbolic": "Create a new Toolbox",
            "media-playback-stop-symbolic": "Stop a Toolbox",
            "dialog-information-symbolic": "View Toolbox Information",
            "preferences-system-symbolic": "Edit Toolbox",
            "utilities-terminal-symbolic": "Open Terminal in Toolbox",
            "system-software-install-symbolic": "Open Application Menu",
            "user-trash-symbolic": "Delete Toolbox",
        }

        pos = 1
        for icon, desc in help_parts.items():
            img = Gtk.Image()
            set_icon_at_small_size(icon, img)
            lbl = Gtk.Label(label=desc)
            lbl.set_xalign(0)

            grid.attach(img, 1, pos, 1, 1)
            grid.attach(lbl, 2, pos, 1, 1)

            pos += 1

        spacer.add(grid)
        box.add(spacer)

        self.show_all()
