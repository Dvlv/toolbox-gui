#!/usr/bin/env bash
find /usr/share/icons -type f -iname "*$1*" >> $2/tb_gui_icon_files.txt
