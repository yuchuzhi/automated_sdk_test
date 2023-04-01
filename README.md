#MCUX SDK自动化测试脚本
##usage:
在当前目录打开cmd terminal，输入以下命令查看脚本支持的参数
python xpc.pyc --help

optional arguments:
  -h, --help            show this help message and exit
  
  -id ID                job id，可选参数，是一个数字字符串，一般是jenkins任务的job id
  
  --platform PLATFORM   specific platform when debug run task 指定板子的名字
  
  --target TARGET       specific build target指定编译的target，也就是debug/release这样的值，可以指定多个，多个target之间用","隔开，比如说debug,release
  
  --apps APPS           specific build 指定编译的程序名字，可以指定单个，也可以是多个，多个程序名字之间用","隔开，比如说hello_world,iled_blinky
  
  --sdk SDK             specific sdk package path 指定sdk 包的地址
  
  --ides IDES           specific build 指定编译的ide名字
  
  --task_type TASK_TYPE specific task type(0: build only,1: build and run,2: run only)指定任务的类型
  
  --flash               fetch binary from server then flash it to board只下载不测试
  
  --filepath FILEPATH   specify the elf file path for run only test.在只下载的情况下，指定待下载的文件路径
