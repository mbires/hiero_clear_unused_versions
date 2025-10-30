# -*- coding: utf-8 -*-
import nuke

menubar = nuke.menu("Nuke")

# Custom Tools Menu
m = menubar.addMenu("BiresTools")
m.addCommand("Clear Offline Media", "import MB_clear_unused_version; MB_clear_unused_version.find_and_delete_unused_versions()")
