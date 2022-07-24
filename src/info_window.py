from app import Gtk


class InfoWindow(Gtk.MessageDialog):
    def __init__(self, parent, toolbox: str, info: dict):
        super().__init__(title=f"Info for {toolbox}", transient_for=parent, flags=0)

        self.add_buttons(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

        box = self.get_content_area()

        spacer = Gtk.Box(spacing=10)
        spacer.set_border_width(10)

        grid = Gtk.Grid()
        grid.set_column_spacing(20)

        labels = []
        for lbl in ["ID", "Status", "Image", "Created At"]:
            l = Gtk.Label()
            l.set_markup(f"<b>{lbl}:</b>")
            labels.append(l)

        grid.attach(labels[0], 1, 1, 1, 1)
        grid.attach(Gtk.Label(label=info["container_id"]), 1, 2, 1, 1)

        grid.attach(labels[1], 2, 1, 1, 1)
        grid.attach(Gtk.Label(label=info["status"]), 2, 2, 1, 1)

        grid.attach(labels[2], 3, 1, 1, 1)
        grid.attach(Gtk.Label(label=info["image"]), 3, 2, 1, 1)

        grid.attach(labels[3], 4, 1, 1, 1)
        grid.attach(Gtk.Label(label=info["created_at"]), 4, 2, 1, 1)

        spacer.add(grid)
        box.add(spacer)

        self.show_all()
