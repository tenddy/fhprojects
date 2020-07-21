#!/usr/bin/env python
# coding=UTF-8
'''
@Desc:
    通过企业微信发送消息
    API参考：https://work.weixin.qq.com/api/doc
@Author: Teddy.tu
@Version: V1.0
@EMAIL: teddy_tu@126.com
@License: (c)Copyright 2019-2020, Teddy.tu
@Date: 2020-04-16 13:47:03
@LastEditors: Teddy.tu
@LastEditTime: 2020-04-17 17:10:53
'''
# -*- coding: utf-8 -*-
import requests
import sys
import os
import json
import logging

WECHAT_CORPID = 'ww128cee9c3fb28c0f'
ZABBIX_APPSECRET = 'EDwMHZIGXq2uAduPRVhhySXuDyyTkuKnKXUFFfK5bms'
ZABBIX_AGENTID = 1000002


class SendMsgByWeChat():
    def __init__(self, agentid=ZABBIX_AGENTID,  appsecret=ZABBIX_APPSECRET, corpid=WECHAT_CORPID, logfile=None):
        self.agentid = agentid  # 应用ID
        self.appsecret = appsecret  # 应用appsecret
        self.corpid = corpid  # 企业微信ID

        # 记录log日志
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s, %(filename)s, %(levelname)s, %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S', filename=os.path.join('/tmp', 'weixin.log'), filemode='a')

        # accesstoken
        self.accesstoken = None

    def __del__(self):
        pass

    def getAccesstoken(self):
        """
        获取accesstoken
        TODO:
        增加缓存access_token，以减少重复获取access_token
        access_token的有效期通过返回的expires_in来传达，正常情况下为7200秒（2小时），有效期内重复获取返回相同结果，
        过期后获取会返回新的access_token。由于企业微信每个应用的access_token是彼此独立的，所以进行缓存时需要区分应用来进行存储。

        """
        token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + self.corpid + '&corpsecret=' + self.appsecret
        req = requests.get(token_url)
        errcode = req.json()['errcode']
        if errcode == 0:
            self.accesstoken = req.json()['access_token']

        return bool(errcode == 0)

    def getUsers(self, userid=None):
        """
        获取成员列表
        """
        userid = 'TuDongDong' if userid is None else userid  # 当前管理员userid为 'TuDongDong'
        url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token=' + self.accesstoken + '&userid=' + userid
        req = requests.get(url)
        print("users:", req.json())

    def getParty(self, id=''):
        """
        获取部门列表
        """
        url = 'https://qyapi.weixin.qq.com/cgi-bin/department/list?access_token=' + self.accesstoken
        req = requests.get(url)
        print("party:", req.json())

    def getTags(self, tagid=''):
        """
        获取标签列表
        """
        tagid = 'zabbix'
        url = 'https://qyapi.weixin.qq.com/cgi-bin/tag/get?access_token=' + self.accesstoken + '&tagid=' + tagid
        req = requests.get(url)
        print("tags:", req.json())

    def sendMsg(self, msg, **args):
        '''
        发送消息
        '''
        # 如果accesstoken为空，重新获取accesstoken
        if self.accesstoken is None:
            self.getAccesstoken()

        # 消息url
        msgsend_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.accesstoken
        content = {}

        # 消息发送对象，必须选择一个
        if 'touser' in args.keys():
            content["touser"] = args['touser']

        if 'toparty' in args.keys():
            content["toparty"] = args['toparty']

        if 'totag' in args.keys():
            content["totag"] = args['totag']

        # 默认消息发送所有成员
        if ('touser' not in args.keys()) and ('toparty' not in args.keys()) and ('totag' not in args.keys()):
            content["touser"] = '@all'

        # 消息格式，默认为文本格式
        content["msgtype"] = args['msgtype'] if 'msgtype' in args.keys() else 'text'
        content["agentid"] = self.agentid

        # 消息内容
        content["text"] = {"content": msg}
        # 是否是保密消息，默认否
        content["safe"] = 0

        req = requests.post(msgsend_url, data=json.dumps(content))

        errcode = req.json()['errcode']
        if errcode != 0:
            logging.error("ErrCode: ", errcode, ";ErrMsg: ", req.json()['errmsg'])
        else:
            logging.info('message: ' + msg)


def sendMsgWechat(message, touser='@all', toparty=None, agentid=1000002):
    """
    函数功能：
        通过企业微信发送消息
    """

    # 企业ID
    corpid = 'ww128cee9c3fb28c0f'
    # 应用 secrect
    appsecret = 'EDwMHZIGXq2uAduPRVhhySXuDyyTkuKnKXUFFfK5bms'
    # 应用ID
    # agentid = 10002

    # 获取accesstoken
    token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + corpid + '&corpsecret=' + appsecret
    req = requests.get(token_url)
    accesstoken = req.json()['access_token']

    # 发送消息url
    msgsend_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + accesstoken

    # touser = '@all'  # 企业微信用户账号，在Zabbix用户的media中设置。
    subject = "alarm"
    toparty = '@all'
    # message = sys.argv[2] + "\n\n" + sys.argv[3]

    print("message:", message)
    # 消息参数使用说明：
    # @touser：企业微信用户账号
    # @toparty：部门ID列表
    # @totag：标签列表
    # @msgtype：消息类型，此处默认为text
    # @agentid：企业应用ID
    # @content： 消息内容
    # @safe： 是否是保密消息，1表示是，默认为0

    params = {
        "touser": touser,
        # "toparty": toparty,
        "msgtype": "text",
        "agentid": agentid,
        "text": {
            "content": message
        },
        "safe": 0
    }
    req = requests.post(msgsend_url, data=json.dumps(params))
    logging.info('sendto:' + touser + ';;subject:' + subject + ';;message:' + message)


if __name__ == "__main__":
    # msg = sys.argv[1]
    # users = sys.argv[2]
    # sendMsgWechat(message=msg, touser=users)
    sendMsg = SendMsgByWeChat()
    sendMsg.getAccesstoken()
    sendMsg.getUsers()
    sendMsg.getParty()
    sendMsg.getTags()
    sendMsg.sendMsg("test")
