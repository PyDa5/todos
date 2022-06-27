# -*- coding: utf-8 -*-
"""
@File    : middleware.py
@Author  : 大五学长
@Time    : 2022/5/15 20:48
@desc    :
         
"""
import logging

from django.http import HttpRequest
from django.http.response import HttpResponsePermanentRedirect
from django.middleware.common import MiddlewareMixin

debugger = logging.getLogger('debugger')
