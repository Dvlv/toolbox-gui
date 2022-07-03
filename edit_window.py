import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class EditWindow(Gtk.MessageDialog):
    def __init__(self, parent, toolbox):
        super().__init__(title=f"Edit {toolbox}", transient_for=parent, flags=0)

        save_btn = Gtk.Button(label="Save")

        self.add_action_widget(save_btn, Gtk.ResponseType.OK)

        self.add_buttons(
              Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL
        )

        l1 = Gtk.Label(label="Toolbox Name:")
        self.toolbox_name = Gtk.Entry(text=toolbox)

        box = self.get_content_area()
        box.add(l1)
        box.add(self.toolbox_name)

        self.show_all()

    def get_entered_name(self):
        return self.toolbox_name.get_text()