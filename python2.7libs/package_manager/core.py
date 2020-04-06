import sys

import hou

IS_WINDOWS_OS = sys.platform.startswith('win')
IS_MAC_OS = sys.platform.startswith('darwin')
IS_LINUX_OS = sys.platform.startswith('linux')
IS_SUPPORTED_OS = IS_WINDOWS_OS or IS_MAC_OS or IS_LINUX_OS
