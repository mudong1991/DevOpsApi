# -*- coding: UTF-8 -*-
__author__ = 'MD'
from channels.routing import route, include
from Operations import consumers

chat_routing = [
    route("websocket.connect", consumers.ws_conntect),  # 当WebSocket请求连接上时调用consumers.ws_connect函数
    route("websocket.receive", consumers.ws_message),  # 当WebSocket请求发来消息时。。。
    route("websocket.disconnect", consumers.ws_disconnect),  # 当WebSocket请求断开连接时。。。
]

channel_routing = [
    # route('http.request', consumers.http_consumer),
    include(chat_routing, path=r"^/chat")
]