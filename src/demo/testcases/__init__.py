import os
import sys
from lib import settings
# print("file", __file__)
sys.path.append("/".join(__file__.split("/")[:3]))
# print("syspath:", sys.path)
# print("getcwd", os.getcwd())

settings.TESTCASE_PATH = "/".join(__file__.split("/")[:-2])
settings.LOG_PATH = "/".join(__file__.split("/")[:-2]) + "/log"
settings.CAP_PATH = "/".join(__file__.split("/")[:-2]) + "/capture"
