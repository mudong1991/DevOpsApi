# -*- coding: UTF-8 -*-
from __future__ import print_function

import time
__author__ = 'MD'
from django.http import HttpResponse
from channels import Group
from channels.handler import AsgiHandler


def http_consumer(message):
    # Make standard HTTP response - access ASGI path attribute directly
    response = HttpResponse("Hello world! You asked for %s" % message.content['path'])
    # Encode that response into message format (ASGI)
    for chunk in AsgiHandler.encode_response(response):
        message.reply_channel.send(chunk)


# 当连接上时，发回去一个connect字符串
def ws_conntect(message):
    # Accept the connection
    message.reply_channel.send({"accept": True})
    # Add to the chat group
    Group("chat").add(message.reply_channel)


# 将发来的信息原样返回
def ws_message(message):
    while True:
        Group("chat").send({
            "text": message.content['text'],
        }, immediately=True)
        time.sleep(4)


# 断开连接时发送一个disconnect字符串，当然，他已经收不到了
def ws_disconnect(message):
    Group("chat").discard(message.reply_channel)