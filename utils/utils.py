#
# cloudwatch-thing general utils
#
# Author: Konrad Markus <konker@iki.fi>
#
#------------------------------------------------------------------------

import os


def is_rpi():
    uname = os.uname()
    return uname.machine.startswith('armv6')

