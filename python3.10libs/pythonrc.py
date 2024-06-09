from datetime import timedelta

import hou

if hou.isUIAvailable():
    from time import time

    from package_manager import UpdateOptions, check_for_updates

    options = UpdateOptions()
    current_time = time()
    # It should be over 4 hours since the last check.
    if options.check_on_startup() and current_time - options.last_check_time() > timedelta(hours=4).total_seconds():
        check_for_updates()
