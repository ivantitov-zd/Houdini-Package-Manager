from __future__ import print_function

if hou.isUIAvailable():
    from time import time

    from package_manager import UpdateOptions, checkForUpdates

    options = UpdateOptions()
    current_time = time()
    # It should be over 4 hours since the last check.
    if options.checkOnStartup() and current_time - options.lastCheckTime() > 14400:
        checkForUpdates()
