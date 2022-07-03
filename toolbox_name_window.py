import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class ToolboxNameWindow(Gtk.MessageDialog):
    def __init__(self, parent):
        super().__init__(title="Toolbox Name", transient_for=parent, flags=0)

        create_btn = Gtk.Button(label="Create")

        self.add_action_widget(create_btn, Gtk.ResponseType.OK)

        self.add_buttons(
              Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL
        )

        self.format_secondary_text(
            "Enter the name of your new toolbox"
        )

        self.toolbox_name = Gtk.Entry()

        box = self.get_content_area()
        box.add(self.toolbox_name)

        self.show_all()

    def get_entered_name(self):
        return self.toolbox_name.get_text()