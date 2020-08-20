# 项目说明
​	烽火通信宽带接入产出线接入网自动化测试框架
  Git地址：git@10.182.32.235:/home/git/fhat/fhat.git, 密码git
# 文件说明

F:\FHAT\fhprojects>
├─lib （测试用例库文件）
│  ├─oltlib (OLT操作命令行接口)
│  ├─public（共用接口，Telnet，TL1，SNMP， log日志等）
│  ├─stclib（Sprient TestCenter仪表接口）
│  ├─tools （其他共用工具）

├─src （测试场景用例目录）
│  └─demo （测试场景名称）
│      ├─capture   （抓包）
│      ├─instruments （仪表配置)
│      ├─log (log日志)
│      ├─parameters （其他配置文件）
│      └─testcases （测试用例）

# 项目依赖

1. [pyshark](https://github.com/KimiNewt/pyshark/) 

   安装pyshark时, 可能提示需要按照lxml，需要根据python版本，安装相应的依赖包。

   下载对应的*.whl文件，[Unofficial Windows Binaries for Python Extension Packages](https://www.lfd.uci.edu/~gohlke/pythonlibs/) 

   

# 使用说明

