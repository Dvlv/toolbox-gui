# Toolbox GUI
A GUI manager for your toolboxes, made with Python and GTK.

![screenshot](screenshot.png)

## Functionality
- :heavy_plus_sign: - Create new Toolbox.
- ⏹ - Stop Toolbox (only appears if running).
- :information_source: - View Toolbox information.
- :gear: - Change Toolbox Settings (name).
- :computer: - Open a terminal in Toolbox
- :package:
    - Run a Command inside Toolbox
    - View Applications inside Toolbox / Copy Applications to Host
    - Install an RPM File inside Toolbox
    - Update Toolbox
- :wastebasket: - Delete Toolbox

(Icons may differ based on your icon theme)

## Running
Clone this repo, then execute `./toolbox-gui`. A Silverblue / Kinoite installation should come with the necessary python dependencies out-of-the-box.

## TODO
- [ ] Docstrings, move functions about
- [ ] Check and create ~/.local/share/applications if not exists
- [ ] Initial download requires console use, look for -y flag in toolbox create
- [ ] Copy icons over when moving desktop file
- [ ] Icon
- [ ] Flatpak
- [x] Icon size hack for the main window buttons (Kinoite)
- [x] Check Kinoite
