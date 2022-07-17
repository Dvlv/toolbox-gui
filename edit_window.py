from app import Gtk

class EditWindow(Gtk.MessageDialog):
    def __init__(self, parent, toolbox):
        super().__init__(title=f"Edit {toolbox}", transient_for=parent, flags=0)

        self.add_buttons(
              Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL
        )

        save_btn = Gtk.Button(label="Save")
        self.add_action_widget(save_btn, Gtk.ResponseType.OK)

        l1 = Gtk.Label(label="Toolbox Name:")
        self.toolbox_name = Gtk.Entry(text=toolbox)
        self.toolbox_name.connect("activate", lambda e: self.emit("response", Gtk.ResponseType.OK))

        box = self.get_content_area()

        spacer = Gtk.Box(spacing=10)
        spacer.set_border_width(10)

        spacer.add(l1)
        spacer.add(self.toolbox_name)

        box.add(spacer)

        self.show_all()

    def get_entered_name(self):
        return self.toolbox_name.get_text()
