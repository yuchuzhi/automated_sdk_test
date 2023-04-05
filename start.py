import sys
import os
import re
import uuid
import math
import logging
import argparse
import pathlib
import requests
import click
from click import progressbar
from zipfile import ZipFile
from cfg_parer import CfgParser
from runner import Runner
from builder import Builder
from urllib.parse import urlparse
from urllib.request import HTTPError, urlretrieve
from redmine.redmine_cli import RedmineCli
from mcutool.compilers.result import Result
from mcutool.projects_scanner import find_projects
from settings import APP_TEST_PATH, LOCAL_SCRIPT


BUG_SUBMMIT = False
REDMINE_URL = "http://localhost/redmine"
REDMINE_USERNAME = "username"
REDMINE_PASSWD = "password"
DEFAULT_REDMINE_PRJ_ID = 1
DEFAULT_REDMINE_SUBJECT = "issue"
DEFAULT_HTTP_FILE_SERVER_AUTH = ("ubuntu", "Happy123")


@click.command()
@click.option("-p", "--platform", default="evkbimxrt1050", help='specific platform when debug run task')
@click.option("-f", "--filepath", default="hello_world.out", help='specific filepath to flash into board')
def flash(platform, filepath):
    print(platform, filepath)
    cfg = CfgParser()
    if os.path.exists(filepath):
        if not platform:
            raise ValueError(f"invalid board name:{platform}")

        board = cfg.get_board(platform)
        return board.programming(filepath)
    else:
        raise ValueError(f"invalid binary file path:{filepath}")


def get_projects(sdk_root_path, applist, ides=["mcux"]):
    """快速的从SDK根目录中解析到工程文件的路径
    """
    #获取所有工程文件的路径，为每个工程文件创建一个工程类的实例
    projects, count = find_projects(sdk_root_path)
    expect_prjs = {}

    #过滤出指定的工程类实例的列表
    for idename, project_list in projects.items():
        if idename in ides:
            expect_prjs[idename] = [p for p in project_list if p.name in applist]

    return expect_prjs

def get_boardname(sdk_path, project_path):
    boardname = re.findall(f"{sdk_path}/boards/(\w+)", project_path.replace("\\", "/"))[0]
    return boardname


@click.command(name="run")
#@click.option("-id", default="11", help='specific a job id')
@click.option("-t", "--target", default="release", help='specific build target')
@click.option("-p", "--platform", default="evkbimxrt1050", help='specific board name to test')
@click.option("--appname", default="hello_world", help='specific app name list to build')
@click.option("-f", "--filepath", default="hello_world.out", help='specific filepath to download')
def run_test(filepath, platform, appname, target):
    generate_work_path("1")
    runner = Runner()
    runner.init(platform, appname, target)
    ret = runner.run_test(filepath)
    ret_value = 0
    if "pass" == ret.lower():
        logging.info('{:-^48}'.format(f" Test result =  {ret} "))
    else:
        logging.error('{:-^48}'.format(f" Test result =  {ret} "))
        ret_value = 1

    return ret_value


@click.command()
@click.option("--job_id", default="11", help='specific a job id')
@click.option("--sdk", default="", help='specific sdk package path')
@click.option("-t", "--targets", default="release", help='specific build target')
@click.option("--apps", default="hello_world,iled_blinky", help='specific app name list to build')
@click.option("--ides", default="mcux", help='specific ide name list to build')
def build(job_id, targets, apps, ides, sdk):
    results = []
    targets = targets.split(",")
    apps = apps.split(",")
    ides = ides.split(",")
    workspace = generate_work_path(job_id)
    sdk_path = get_sdk_path(sdk)

    projects = get_projects(sdk_path, apps, ides=ides)
    output_files = []
    #挨个编译工程列表的所有工程
    for idename, project in projects.items():
        for prj in project:
            for target in targets:
                builder = Builder()
                output_store_path = f"{APP_TEST_PATH}/{prj.boardname}/"
                if not os.path.exists(output_store_path):
                    os.makedirs(output_store_path)

                #初始化builder的属性
                builder.init(idename, target, output_store_path, workspace, prj.name)
                #用待编译的工程实例替换掉编译器绑定的工程类实例
                builder.compiler.Project = prj

                #开始编译
                result = builder.build()
                ret_value = result.result.value

                #将每次的编译结果都添加到结果列表里
                results.append(ret_value)
                #打印每次编译结果
                if ret_value == 0:
                    build_output_file = builder.post_build(result)
                    output_files.append((build_output_file, prj.boardname, prj.name, target))
                    logging.info('{:-^48}'.format(f" Build result =  {result.result.name} "))
                else:
                    #如果提交bug的标志是True，提交一个build 失败的bug到redmine.
                    if BUG_SUBMMIT:
                        redmine_create_issue(DEFAULT_REDMINE_PRJ_ID, DEFAULT_REDMINE_SUBJECT)
                    logging.error('{:-^48}'.format(f" Build result =  {result.result.name} "))

    total = len(results)
    counter_fail = 0
    counter_warnning = 0
    counter_pass = 0
    for value in results:
        if value == 0:
            counter_pass += 1
        elif value == 2:
            counter_warnning += 1
        else:
            counter_fail += 1

    logging.info(f"Total build: {total}")
    logging.info(f"Build Passes: {counter_pass}")
    logging.info(f"Build Warnnings: {counter_warnning}")
    logging.info(f"Build Fails: {counter_fail}")

    ret = 1
    if counter_fail == 0:
        ret = 0

    return ret, output_files


@click.command(name="buildrun")
@click.pass_context
@click.option("--job_id", default="11", help='specific a job id')
@click.option("--sdk", default="", help='specific sdk package path')
@click.option("-t", "--targets", default="release", help='specific build target')
@click.option("--apps", default="hello_world,iled_blinky", help='specific app name list to build')
@click.option("--ides", default="mcux", help='specific ide name list to build')
def build_run(ctx, job_id, targets, apps, ides, sdk):
    run_results = []
    ret, output_files = ctx.invoke(build, job_id=job_id, targets=targets, apps=apps, ides=ides, sdk=sdk)
    for outputfile in  output_files:
        run_result = ctx.invoke(run_test, filepath=outputfile[0], platform=outputfile[1], appname=outputfile[2], target=outputfile[3])
        run_results.append(run_result)

    total = len(run_results)
    counter_fail = 0
    counter_pass = 0
    for value in run_results:
        if value == 0:
            counter_pass += 1
        else:
            counter_fail += 1

    logging.info(f"Total Run: {total}")
    logging.info(f"Run Passes: {counter_pass}")
    logging.info(f"Run Fails: {counter_fail}")

    ret = 1
    if counter_fail == 0:
        ret = 0

    return ret

def get_sdk_path(sdkpath):
    cfg = CfgParser()
    sdkpath
    sdk_store_path = cfg.get_sdk_rootpath().replace("\\", "/")
    sdk_local_path = sdkpath.split(",")
    if sdkpath.startswith("http://") or sdkpath.startswith("https://"):
        sdk_local_path = []
        for sdk_path in sdkpath.split(","):
            sdk_local_path_download = download_package(sdk_path, f"{LOCAL_SCRIPT}/downloads")
            sdk_local_path.append(sdk_local_path_download)

    actual_sdk_path = extract(sdk_local_path, sdk_store_path)
    return actual_sdk_path[0]


def download_package(url, dstdir):
    def _convert_size(size_bytes):
        if size_bytes == 0:
            return '0B'
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes/p, 2)
        return '%s %s' % (s, size_name[i])

    identifier = "._down_%s" % uuid.uuid4().hex[:6]
    tempfile = None
    parsed_uri = urlparse(url)
    filename = os.path.basename(parsed_uri.path)

    # download from http or https
    try:
        http_auth = DEFAULT_HTTP_FILE_SERVER_AUTH

        # Add parameter auth because access to HTTP File Server requires password authentication.
        response = requests.get(url, stream=True, auth=http_auth, timeout=20*60, allow_redirects=True, verify=False)
        if response.status_code == 404:
            raise HTTPError("404 Not Found")

        try:
            d = response.headers["content-disposition"]
            filename = re.findall("filename=(.+)", d)[0].replace("\"", "")
        except Exception:
            pass

        totalsize = int(response.headers["Content-Length"])
        downloadfile = os.path.join(dstdir, filename)
        tempfile = downloadfile + identifier

        if not os.path.exists(dstdir):
            os.makedirs(dstdir)

        if os.path.exists(tempfile):
            os.remove(tempfile)

        chunksize = 4*1024
        logging.info("{0}, size {1}".format(filename, _convert_size(totalsize)))

        length = (totalsize/chunksize) + 1
        with progressbar(response.iter_content(chunksize), length=length, label='downloading') as bar:
            with open(tempfile, 'wb') as fobj:
                for buf in bar:
                    if buf:
                        fobj.write(buf)

        if totalsize > 0 and totalsize != os.path.getsize(tempfile):
            raise IOError("Download error")

        # before rename, make sure file name is not exists! otherwise it will raise
        # WindowsError: [Error 183] Cannot create a file when that file already exists
        try:
            if os.path.exists(downloadfile):
                os.remove(downloadfile)
        except WindowsError:
            split_filename = filename.split('.')
            filename = "_".join(split_filename[:-1]) + "_1." + split_filename[-1]
            downloadfile = os.path.join(dstdir, filename)

        os.rename(tempfile, downloadfile)
    finally:
        if tempfile and os.path.exists(tempfile):
            os.remove(tempfile)

    return downloadfile

def extract(filepaths, dest_path):
    store_folder_path = []
    for filepath in filepaths:
        filename = os.path.basename(filepath).split(".")[0]
        file_dest_path = f"{dest_path}/{filename}"
        logging.info(f"extract sdk file {filepath} to {file_dest_path}")
        if filepath.endswith(".zip"):
            zipFile = ZipFile(filepath, "r")
            for file in zipFile.namelist():
                zipFile.extract(file, file_dest_path)
            zipFile.close()
            store_folder_path.append(file_dest_path)
    return store_folder_path


def redmine_create_issue(project_id, subject):
    """create a issue to redmine"""
    redmine = RedmineCli()
    redmine.connect(REDMINE_URL, username=REDMINE_USERNAME, password=REDMINE_PASSWD)
    redmine.create_issue(project_id, subject)

def generate_work_path(job_id):
    workspace = pathlib.Path(LOCAL_SCRIPT).joinpath(f".workspaces/{job_id}").as_posix()
    log_path = pathlib.Path(workspace).joinpath("logs").as_posix()
    if not os.path.exists(workspace):
        os.makedirs(workspace)
    if not os.path.exists(log_path):
        os.makedirs(log_path)    

    cfg = CfgParser()
    log_file = f"{workspace}/logs/test_log.log"
    cfg.init_log(log_file)
    return workspace


@click.group()
def cli():
    pass


cli.add_command(flash)
cli.add_command(build)
cli.add_command(build_run)
cli.add_command(run_test)



if __name__ == "__main__":
    if sys.version_info[0] < 3:
        print("require python >= 3.6")
        sys.exit(1)

    cli()
