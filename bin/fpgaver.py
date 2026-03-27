#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from lib.FPGADevice import FPGADevice

fpga = FPGADevice('/dev/uio0')

ver = fpga.bitstream_version()

print(f"\n# FPGA bitstream: release/tag: {ver['release']}, build: {ver['build_date']}/{ver['build_time']}, commit: {ver['commit_date']}/{ver['commit_hash']}, variant: {ver['variant']}\n")
