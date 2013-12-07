xbmc-desktop-launcher-generator
===============================

XBMC script that converts XDG-compliant desktop launchers to program addons.
Works with desktop entries created by Gnome, KDE, XFCE, etc.

Installation
------------

Copy script.desktop.launcher.generator/ to your xbmc addons directory.
Appears as "Desktop Launcher Generator" in XBMC.

Known limitations
-----------------

* Does not auto-update contents, requires manual start.
* If a launcher is deleted while XBMC is running, it won't disappear from
addon list until restart.
* Needs icon.
