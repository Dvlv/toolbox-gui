from app import Gtk


class ToolboxNameWindow(Gtk.MessageDialog):
    def __init__(self, parent, toolboxes):
        super().__init__(title="Toolbox Name", transient_for=parent, flags=0)

        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)

        create_btn = Gtk.Button(label="Create")
        self.add_action_widget(create_btn, Gtk.ResponseType.OK)

        sec_text = "Enter the name of your new toolbox"
        if not len(toolboxes):
            sec_text += "\nNote: Downloading the container image may take some time."

        self.format_secondary_text(sec_text)

        self.toolbox_name = Gtk.Entry()
        self.toolbox_name.connect(
            "activate", lambda e: self.emit("response", Gtk.ResponseType.OK)
        )

        box = self.get_content_area()

        spacer = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        spacer.set_border_width(10)
        spacer.add(self.toolbox_name)
        box.add(spacer)

        self.show_all()

    def get_entered_name(self):
        return self.toolbox_name.get_text()

    def show_already_exists_message(self):
        self.format_secondary_text(
            f"Enter the name of your new toolbox\n\nError: A toolbox called {self.get_entered_name()} already exists!"
        )
