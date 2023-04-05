import os
import json
import pathlib
import importlib
import logging
import logging.config as log_config
from mcutool.compilers import compilerfactory,factory
from settings import CONFIGURATION_PATH, LOCAL_SCRIPT
import xml.etree.cElementTree as ET


support_toolchain = [
    "mcux"
]

class CfgParser(object):
    def __init__(self):
        self.xmlRoot = ET.parse(CONFIGURATION_PATH).getroot()

    def get_toolchain(self, idename):
        # 安装路径配置在配置文件中，这里要从配置文件中读取ide的安装路径。
        ide_path = self.xmlRoot.find(f"IDE/{idename}").attrib.get("Path")
        # 调用简单工厂模式得到ide类模块。
        ide_module = factory(idename)
        # 从类模块中得到他的“Compiler”属性
        toolchain = getattr(ide_module, "Compiler")
        # 返回ide实例
        return toolchain(path=ide_path)

    def get_sdk_rootpath(self):
        return self.xmlRoot.find("Local/sdk_root_path").text

    def get_board(self, boardname):
        boardmodule = importlib.import_module(f"boards.{boardname}")
        board_obj = getattr(boardmodule, "Board")
        board_config = {}
        with open(f"{LOCAL_SCRIPT}/config/{boardname}.board", "r") as jf:
            board_config = json.load(jf)
        
        devicename = board_config["devicename"]
        debugger_type = board_config["debugger"]["type"]
        usbid = board_config["debugger"]["usbid"]
        gdbport = board_config["debugger"]["gdbport"]
        ports = board_config["ports"]
        board = board_obj(name=boardname, devicename=devicename, usbid=usbid, debugger_type=debugger_type, gdbport=gdbport)
        for serial_para in ports:
            board.set_serial(serial_para["port"], serial_para["baudrate"])

        return board

    def init_log(self, logfile):
        # config logging module
        log_conf = pathlib.Path(LOCAL_SCRIPT).joinpath("config/logger.conf").as_posix()
        with open(logfile, "w+") as lf:
            pass

        log_config.fileConfig(log_conf, disable_existing_loggers=False, defaults=dict(log_file=logfile))
