import os
import subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

def get_output(cmd: str):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    return proc.stdout.read().decode("utf-8")

def create_toolbox_button(icon_name: str, tooltip: str, func):
    icon = Gtk.Image()
    icon.set_from_icon_name(icon_name, Gtk.IconSize.BUTTON)

    btn = Gtk.Button(label=None, image=icon)
    btn.connect("clicked", lambda b: func())
    btn.set_tooltip_text(tooltip)

    return btn

def execute_delete_toolbox(toolbox: str):
    subprocess.run(["podman", "stop", toolbox])
    subprocess.run(["toolbox", "rm", toolbox])

def fetch_all_toolboxes():
    cmd = 'podman ps -a --format={{.Names}}||{{.Image}}||{{.Status}}||{{.ID}}'
    toolboxes = get_output(cmd.split(" "))

    toolboxes = toolboxes.split("\n")[:-1]

    retval = []

    for tb in toolboxes:
        name, image, status, tb_id = tb.split("||")
        image_num = image.split(':')[-1]
        retval.append((name, image_num, status, tb_id))

    return retval