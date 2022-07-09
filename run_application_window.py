import threading
import gobject
from functools import partial

from main import Gtk, GLib

class ImgFetchThread(threading.Thread):
    def __init__(self, master):
        super().__init__()
        self.master = master

    def run(self):
        from utils import get_icon_from_desktop
        
        for app in self.master.imgs.keys():
            icon = get_icon_from_desktop(self.master.toolbox, app)
            self.master.imgs[app].set_from_icon_name(icon, Gtk.IconSize.BUTTON)
            self.master.add_icon_to_cache(app, icon)

        return


class RunApplicationWindow(Gtk.MessageDialog):
    def __init__(self, parent, toolbox, apps: list):
        super().__init__(title=f"Run Application from {toolbox}", transient_for=parent, flags=0)
        self.apps = apps
        self.toolbox = toolbox
        self.parent = parent

        self.add_buttons(
              Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL
        )

        box = self.get_content_area()

        spacer = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        spacer.set_border_width(10)

        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)

        self.chosen_app = None
        self.imgs = {}
        for idx, app in enumerate(self.apps):
            nice_app = app.replace("-", " ")
            nice_app = nice_app.replace("_", " ")
            nice_app = nice_app.replace(".desktop", "")
            nice_app = nice_app.title()

            img = Gtk.Image()
            if app in self.parent.icon_cache:
                img.set_from_icon_name(self.parent.icon_cache[app], Gtk.IconSize.BUTTON)
            else:
                self.imgs[app] = img

            lbl = Gtk.Label(label=nice_app)
            lbl.set_xalign(0)

            btn = Gtk.Button(label="Open")
            btn.connect("clicked", partial(self.on_app_chosen, app))

            i_btn = Gtk.Button(label="Add to Menu")
            i_btn.connect("clicked", partial(self.on_app_chosen, app))

            grid.attach(img, 1, idx, 1, 1)
            grid.attach(lbl, 2, idx, 1, 1)
            grid.attach(i_btn, 3, idx, 1, 1)
            grid.attach(btn, 4, idx, 1, 1)

        spacer.add(grid)
        spacer.show_all()
        box.add(spacer)

        self.grid = grid

        self.show_all()

        if len(self.imgs):
            self.img_thread = ImgFetchThread(self)
            self.img_thread.start()


    def on_app_chosen(self, app: str, *args):
        self.chosen_app = app
        self.emit("response", Gtk.ResponseType.OK)

    def set_chosen_app(self, app: str):
        self.chosen_app = app

    def get_chosen_app(self):
        return self.chosen_app

    def add_icon_to_cache(self, app: str, icon: str):
        if app not in self.parent.icon_cache:
            self.parent.icon_cache[app] = icon
