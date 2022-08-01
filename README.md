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

## Flatpak
Clone or download this repo, `cd` into the folder, then install like so:

### From Binary
- `flatpak install --user toolbox-gui.flatpak`

### Build From Source
- Install `flatpak-builder` (probably in a Toolbox)
- `flatpak-builder --user --install --force-clean build-dir co.uk.dvlv.toolbox-gui.yml`

## Running (Standalone script)
Clone this repo, then execute `./toolbox-gui`. A Silverblue / Kinoite installation should come with the necessary python dependencies out-of-the-box.

## TODO
- [ ] Icon PNGs


### Future Functionality
- [ ] Help Page
- [ ] About Page
- [ ] Export / Import list of packages (for upgrading)
- [ ] Dist Upgrades (sudo dnf update --releasever=36)
