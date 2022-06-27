# -*- coding: utf-8 -*-
"""
@File    : throtting.py
@Author  : 大五学长
@Time    : 2022/5/17 12:15
@desc    : 限流插件
         
"""
import logging

from rest_framework.request import Request
from rest_framework.throttling import BaseThrottle
debugger = logging.getLogger('debugger')


class EmailCaptchaThrottle(BaseThrottle):
    THROTTLE_RATE = (
        '1/min',
        '3/10min',
        '5/hour',
        '10/day'
    )
    def allow_request(self, request: Request, view):
        """根据Email，一分钟只能发1次，10分钟只能发3次，一小时只能发5次，一天只能发10次"""

        email = request.data.get('email', None)
        if not email:
            return False
        # 解析限流规则
        rates = {}


        cache_key = 'throttle：captcha:{email}'
        # 取出缓存时间戳，截取能作为判定依据的时间戳
        my_cache = [1, 364875, 7349795]
        # 当满足所有限流规则时候，放行；同时将本次请求时间戳压入时间戳列表，截取

        # 若满足所有条件
        """
        1、把缓存时间戳取出来
        2、
        """
        pass
