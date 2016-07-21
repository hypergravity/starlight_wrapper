import os
import sys
import glob
import pkgutil

from .preprocessing import (preprocess_ccm,
                            preprocess_write_spectrum,
                            preprocess_sdss_dr10,
                            preprocess_sdss_dr10_script,
                            preprocess_sdss_dr10_script_print)
from .utils import (StarlightBase,
                    StarlightConfig,
                    StarlightMask,
                    StarlightGrid,
                    StarlightOutput)
from .run import run
from .config import PACKAGE_PATH

# #################### #
# print welcome string #
# #################### #

str_welcome = """
Welcome to use **STARLIGHT_WRAPPER** written by Bo Zhang (bozhang@nao.cas.cn).
Have fun with it!
"""
print(str_welcome)


# #################### #
# print welcome string #
# #################### #

print('@Cham: current package path: %s' % PACKAGE_PATH)

