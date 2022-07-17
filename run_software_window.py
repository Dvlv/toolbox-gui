from app import Gtk

class RunSoftwareWindow(Gtk.MessageDialog):
    def __init__(self, parent, toolbox):
        super().__init__(title=f"Run Command in {toolbox}", transient_for=parent, flags=0)

        self.add_buttons(
              Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL
        )

        save_btn = Gtk.Button(label="Run")
        self.add_action_widget(save_btn, Gtk.ResponseType.OK)

        self.format_secondary_text("Command to run:")

        self.command = Gtk.Entry()
        self.command.connect("activate", lambda e: self.emit("response", Gtk.ResponseType.OK))

        box = self.get_content_area()

        spacer = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        spacer.set_border_width(10)

        spacer.add(self.command)

        box.add(spacer)

        self.show_all()

    def get_entered_command(self):
        return self.command.get_text()
