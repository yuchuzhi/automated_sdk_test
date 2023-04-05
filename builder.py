import os
import pathlib
import logging
from shutil import copyfile
from cfg_parer import CfgParser


class Builder(object):
    def __init__(self):
        self.idename = None
        self.compiler = None
        self.target = None
        self.workspace = None
        self.appname = None
        self.build_log_file = None

    def init(self, idename, app_target, output_path, workspace, appname):
        cfg = CfgParser()
        self.idename = idename
        self.target = app_target
        self.compiler = cfg.get_toolchain(self.idename)
        self.workspace = workspace
        self.appname = appname
        self.output_path = pathlib.Path(output_path).joinpath(f"{self.appname}_{self.target}").as_posix()
        self.build_log_file = os.path.join(self.workspace, f"logs/{self.idename}_{self.appname}_{self.target}_build.log")
        

    def build(self):
        logging.info('{:#^48}'.format(f" Build Start "))
        logging.info('{:-^20}'.format(f" project name: {self.appname} idename: {self.idename} target: {self.target} "))
        build_workspace = f"{self.workspace}/build_workspace_{self.appname}_{self.target}"
        target = self.compiler.Project.map_target(self.target)
        result = self.compiler.build_project(self.compiler.Project, target, self.build_log_file, workspace=build_workspace)
        logging.info('{:=^48}'.format(" Build Log "))
        with open(self.build_log_file, "r") as lf:
            content = lf.read()
            logging.info(content)

        logging.info('{:#^48}'.format(" Build End "))
        return result

    def post_build(self, result):
        filepath = result.output
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        dest_file_path = None
        if os.path.exists(filepath):
            dest_file_path = pathlib.Path(self.output_path).joinpath(os.path.basename(filepath)).as_posix()
            if os.path.exists(dest_file_path):
                os.remove(dest_file_path)
            logging.info(f"copy file from {filepath} to {dest_file_path}")
            copyfile(filepath, dest_file_path)

        return dest_file_path