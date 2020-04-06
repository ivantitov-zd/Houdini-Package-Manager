if hou.isUIAvailable():
    import hdefereval
    from package_manager.github import checkUpdates

    hdefereval.executeDeferred(checkUpdates)
