import xbmc
import subprocess
import glob
import xdg.DesktopEntry
import os
import string
import shutil
import shlex
import errno
import codecs
import PIL.Image
from xml.sax.saxutils import escape
from xml.sax.saxutils import quoteattr

addon_prefix = "script.desktop.launcher."
addon_name = addon_prefix + "generator"
version = "0.1"

# FIXME use Unicode
addon_xml = string.Template(u"""\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id=${addon_dirname} version=${version} name=${addon_name} provider-name=${provider}>
    <requires>
        <import addon="xbmc.python" version="2.1"/>
    </requires>
    <extension point="xbmc.python.script" library="addon.py"/>
    <extension point="xbmc.addon.metadata">
        <platform>linux</platform>
        <summary>${summary}</summary>
        <description>${description}</description>
    </extension>
</addon>
""")

addon_py = string.Template(u"""\
import subprocess
subprocess.Popen(${command})
""")

# We need separate process to get icon name since gtk module succeeds to
# import only the first time the addon is initialized.
get_icon_script = string.Template(u"""\
import sys, gtk
icon_theme = gtk.icon_theme_get_default()
icon_info = icon_theme.lookup_icon('${name}', 256, 0)
if icon_info:
        sys.stdout.write(icon_info.get_filename())
""")

addon_root = xbmc.translatePath("special://home/addons")
watermark = ".generated.by." + addon_name

# Cleanup.
addon_pattern = os.path.join(addon_root, addon_prefix + "*")

for addon in glob.iglob(addon_pattern):
    if os.path.isdir(addon) and os.path.exists(os.path.join(addon, watermark)):
        shutil.rmtree(addon, ignore_errors = True)

# Generate.
desktop_path = subprocess.check_output(["xdg-user-dir", "DESKTOP"]).strip()
desktop_pattern = os.path.join(desktop_path, "*.desktop")

for launcher in glob.iglob(desktop_pattern):
    entry = xdg.DesktopEntry.DesktopEntry(launcher)

    if entry.getHidden() or not entry.getExec():
        continue

    icon_name = entry.getIcon()
    icon_path = ""

    if os.path.isabs(icon_name):
        icon_path = icon_name
    else:
        script = subprocess.Popen(["python", "-"], stdin = subprocess.PIPE,
                stdout = subprocess.PIPE)
        icon_path, _ = script.communicate(get_icon_script.substitute(
            {"name" : icon_name}).encode("utf8"))

    launcher_filename = os.path.basename(launcher)
    name = os.path.splitext(launcher_filename)[0].lower().replace(' ', '-')
    dirname = addon_prefix + name

    xml = addon_xml.substitute({
        "provider" : quoteattr(addon_name),
        "version" : quoteattr(version),
        "addon_dirname" : quoteattr(dirname.decode("utf8")),
        "addon_name" : quoteattr(entry.getName()),
        "summary" : escape(entry.getName()),
        "description" : escape(entry.getComment())})

    py = addon_py.substitute({
        "command" : shlex.split(entry.getExec())})

    dirname = os.path.join(addon_root, dirname)

    try:
        os.makedirs(dirname)

        with codecs.open(os.path.join(dirname, "addon.xml"), "w", encoding = "utf8") as f:
            f.write(xml)
            f.close()

        with codecs.open(os.path.join(dirname, "addon.py"), "w", encoding = "utf8") as f:
            f.write(py)
            f.close()

        if icon_path:
            icon = PIL.Image.open(icon_path)
            icon.save(os.path.join(dirname, "icon.png"), "PNG")

        open(os.path.join(dirname, watermark), "a").close()
    except OSError as e:
        xbmc.log("Generating launcher for %s failed: %s" % (entry.getName(), str(e)))
        pass

xbmc.executebuiltin("UpdateLocalAddons()")
xbmc.executebuiltin("Container.Refresh()")

