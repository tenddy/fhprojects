#!/usr/bin/env python
# coding=UTF-8
'''
@Desc: Sprient TestcCenter Automation API of Python Wrapper
@Author: Teddy.tu
@Version: V1.0
@EMAIL: teddy_tu@126.com
@License: (c)Copyright 2019-2020, Teddy.tu
@Date: 2020-07-16 08:57:06
@LastEditors: Teddy.tu
@LastEditTime: 2020-07-22 16:01:03
'''

from lib.stclib.tclwrapper import TCLWrapper
from lib import settings
from lib.public import fhlog


class STC:
    def __init__(self, tcl="C:/Tcl/bin/tclsh", stcpath=None):
        self._tclsh = TCLWrapper(tcl)
        self._tclsh.start()
        self._stcpath = settings.STC_PATH

    def __del__(self):
        pass

    def load_stc_lib(self):
        """ Initial load SpirentTestCenter package """
        if self._stcpath is None:
            fhlog.logger.error("Not Found Spirent TestCenter Install Path.")
            exit(-1)
        else:
            self._tclsh.eval("set auto_path [linsert $auto_path 0 {%s}]" % self._stcpath)
            
        return self._tclsh.eval("package require SpirentTestCenter")

    def connect(self, stc_addr):
        """ Establishes a connection with a Spirent TestCenter chassis """
        return self._tclsh.eval("stc::connect %s" % stc_addr)

    def disconnect(self, stc_addr):
        """ Removes a connection with a Spirent TestCenter chassis """
        return self._tclsh.eval("stc::disconnect %s" % stc_addr)

    def reserve(self, portList: tuple):
        """
        Description:
            Reserves one or more port groups.

        Syntax:
            reserve portList
        """
        ports = ' '.join(portList)
        tcl_cmd = "stc::reserve [list %s]" % ports
        return self._tclsh.eval(tcl_cmd)

    def release(self, portList: tuple):
        """
        Description:
            Terminates the reservation of one or more port groups.

        Syntax:
            release portList
        """
        ports = ' '.join(portList)
        tcl_cmd = "stc::release [list %s]" % ports
        return self._tclsh.eval(tcl_cmd)

    def create(self, object, under=None, **kargs):
        """
            Description:
                stc::create command

            Syntax:
                create Project|objectType|Path [-under handle] [[-attr value] ...]   [[-objectTypePath [-attrvalue] ...] ...] –relationRef handleList
        """
        cmds = "stc::create %s" % object
        if under is not None:
            cmds += " -under %s" % under

        for k in kargs.keys():
            cmds += " -{0} {1}".format(k, kargs[k])

        fhlog.logger.debug(cmds)

        return self._tclsh.eval(cmds)

    def config(self, handle, **kargs):
        """
        函数功能: Sets or modifies one or more object attributes, or a relation.
        函数参数:
            @param handle(str): handle, DDNPath
            @param kargs(dict):
        返回值: None
        使用说明:
            config handle -attr value [[-attr value] ...]
            config handle -DANPath value [[-DANPath value] ...]
            config handle -objectTypePath -attr value ...
            config DDNPath -attr value [[-attr value] ...]
            config DDNPath -DANPath value [[-DANPath value] ...]
            config DDNPath -objectTypePath -attr value ...
            config handle1 | DDNPath -relationRef handleList
        """
        cmds = "stc::config %s" % handle
        for k in kargs.keys():
            cmds += " -{0} {1}".format(k, kargs[k])
        fhlog.logger.debug(cmds)
        return self._tclsh.eval(cmds)

    def get(self, handle, *args):
        """
        函数功能:
         Returns the value(s) of one or more object attributes or a set of object handles.

        使用说明:
            get handle [-attributeName [...]]
            get handle [-DANPath [...]]
            get DDNPath -attributeName [...]
            get DDNPath -DANPath [...]
            get handle | DDNPath -relationRef [...]
            get handle | DDNPath -children-type
        """
        tcl_cmd = "stc::get {0}".format(handle)

        for attr in args:
            tcl_cmd += " -{0}".format(attr)

        fhlog.logger.debug(tcl_cmd)
        return self._tclsh.eval(tcl_cmd)

    def perform(self, command, **kargs):
        """
        Description:
            Executes a command

        Syntax:
            perform command [[-parameter value] ...]
        """
        tcl_cmd = "stc::perform {0}".format(command)
        for key in kargs.keys():
            tcl_cmd += " -{0} {1}".format(key, kargs[key])
        fhlog.logger.debug(tcl_cmd)
        return self._tclsh.eval(tcl_cmd)

    def subscribe(self, Parent: str, resultType: str, configType: str, **kargs):
        """
        Description

            Enables real-time result collection

        TCL Syntax

            subscribe  -Parent handle
                       -ResultType resultType
                       -ConfigType resultParentType
                        [-FilenamePrefix filenamePrefix]
                        [-ResultParent resultRootType-list]
                        [-Interval seconds]
                        [-ViewAttributeList attrList]
        """
        tcl_cmd = "stc::subscribe -Parent {0} -ResultType {1} -ConfigType {2}".format(Parent, resultType, configType)
        for key in kargs.keys():
            tcl_cmd += " -{0} {1}".format(key, kargs[key])
        fhlog.logger.debug(tcl_cmd)
        return self._tclsh.eval(tcl_cmd)

    def unsubscribe(self, handle):
        """
        函数功能: Removes a previously established subscription.
        函数参数:
            @param
        返回值: None
        使用说明: unsubscribe handle
        """
        return self._tclsh.eval("stc::unsubscribe {0}".format(handle))

    def delete(self, handle: str):
        """
        Description
            Deletes the specified object.

        Syntax
            delete handle
        """
        return self._tclsh.eval("stc::delete {0}".format(handle))

    def apply(self):
        """Apply  test configuration to the Spirent TestCenter chassis"""
        self._tclsh.eval("stc::apply")

    def tcl_eval(self, cmds):
        self._tclsh.eval(cmds)

    def __setattr__(self, key: str, value):

        fhlog.logger.debug("set: key-{0}, value-{1}".format(key, value))

        if key != '_tclsh' and key != '_stcpath':
            self._tclsh.eval("set {0} {1}".format(key, value))
        else:
            super().__setattr__(key, value)
        fhlog.logger.debug(self.__dict__)

    def __getattr__(self, key):
        # print("get: key-{0}".format(key))

        if key != '_tclsh' and key != '_stcpath':
            ret = self._tclsh.eval("puts ${0}".format(key))
            return ret.strip()
        else:
            return self.__dict__[key]

    # def __setitem__(self, item, value):
    #     print("set: key-{0}, value-{1}".format(item, value))

    #     if item != 'tclsh':
    #         # self.tcl_set(key, value)
    #         # super().__setitem__(item, value)
    #         self.tclsh.eval("set {0}() {1}".format(item, value))
    #     else:
    #         super().__setitem__(item, value)

    #     print(self.__dict__)
