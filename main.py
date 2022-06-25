import os
import gi
import subprocess

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Toolbox GUI")
        self.set_default_size(800,640)

        self.toolbox_rows = {}

        self.box = Gtk.Box(spacing=5, orientation=Gtk.Orientation.VERTICAL)
        self.box.set_homogeneous(False)

        toolboxes = self.fetch_all_toolboxes()

        for tb in toolboxes:
            self.render_toolbox_row(tb)

        self.add(self.box)

        self.box.show_all()

    def render_toolbox_row(self, toolbox):
        tb_row = Gtk.Box(spacing=10)
        tb_row.set_border_width(30)
        tb_frame = Gtk.Frame()

        lbl = Gtk.Label(label=toolbox)
        btn = Gtk.Button(label=">")
        btn.connect("clicked", lambda b: self.start_toolbox(toolbox))

        tb_row.pack_start(lbl, True, True, 0)
        tb_row.pack_start(btn, False, False, 10)
        tb_row.show_all()
        tb_frame.add(tb_row)

        self.box.pack_start(tb_frame, False, False, 10)

        self.toolbox_rows[toolbox] = tb_row

    def start_toolbox(self, toolbox):
        # Can't get subprocess to do this properly :/
        os.system('gnome-terminal -- toolbox enter junk')

    def fetch_all_toolboxes(self):
        cmd = 'podman ps -a --format={{.Names}}'
        toolboxes = self.get_output(cmd.split(" "))

        return toolboxes.split("\n")[:-1]

    def get_output(self, cmd: str):
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        return proc.stdout.read().decode("utf-8")

win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
