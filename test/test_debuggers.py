import os
import re
import glob
import platform
from pathlib import Path
from distutils.version import LooseVersion
from unittest import TestCase
from mcutool.debugger import getdebugger


class TestDebugger(TestCase):
    def test_debugger_info(self):
        gdb_path = get_gdb()
        debugger = getdebugger("pyocd", gdbpath=gdb_path, version="10 2021.10")
        print(debugger.gdbpath)
        print(debugger.version)
        print(debugger.name)


def get_gdb():
    possible_gnu_path = [
        r"C:\\Program Files (x86)\\GNU Tools Arm Embedded",
        r"C:\\Program Files (x86)\\GNU Arm Embedded Toolchain",
        r"C:\\Program Files\\GNU Tools Arm Embedded",
        r"C:\\Program Files\\GNU Arm Embedded Toolchain"
    ]

    versions_dict = {}
    for f_path in possible_gnu_path:
        gcc_f_path = glob.glob(f_path + "/*/bin/arm-none-eabi-gcc.exe")
        if gcc_f_path:
            instance_path = os.path.abspath(os.path.join(gcc_f_path[0], "../../"))
        else:
            continue
        osname = platform.system()
        if osname == "Windows":
            version = os.path.basename(instance_path).replace(" ", "-").strip()

        if not version:
            version_content = os.popen("\"{}\" --version".format(gcc_f_path)).read()
            ret = re.search(r"\d\.\d\.\d", version_content)
            if ret is not None:
                version = ret.group()

        if version:
            print("gdb path:", instance_path)
            versions_dict[version] = instance_path

    if not versions_dict:
        raise ValueError("Warning: build tool path invalid!!!")

    latest_v = sorted(versions_dict.keys(), key=lambda v: LooseVersion(v))[-1]

    return Path(versions_dict[latest_v]).joinpath("bin/arm-none-eabi-gcc.exe").as_posix()

