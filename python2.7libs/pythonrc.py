if hou.isUIAvailable():
    from time import time

    from package_manager import UpdateOptions, checkForUpdates

    options = UpdateOptions()
    current_time = time()
    # It should be over 2 hours since the last check.
    if options.checkOnStartup() and current_time - options.lastCheckTime() > 7200:
        checkForUpdates()
        options.setLastCheckTime(current_time)
