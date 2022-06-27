# -*- coding: utf-8 -*-
"""
@File    : authentication.py
@Author  : 大五学长
@Time    : 2022/5/16 20:40
@desc    : 用户认证类
"""
import logging
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request

from api.token import decrypt_client_jwt
from api.models import TUser

debugger = logging.getLogger('debugger')


class AnonymousUser:
    id = -1
    username = 'anonymous'

    def __init__(self, token=None):
        self.token = token


class UserAuthentication(BaseAuthentication):
    def authenticate(self, request: Request):
        """用户认证类"""
        jwt_str = request.COOKIES.get('token', None)
        # 客户端无token
        if not jwt_str:
            return None, None
        # 客户端为匿名用户
        payload = decrypt_client_jwt(jwt_str)
        token = payload.get('token', None)
        if 'uid' not in payload:
            return AnonymousUser(jwt_str), token
        # 用户不存在
        uid = payload.get('uid')
        user = TUser.objects.filter(id=uid).first()
        if not user:
            return AnonymousUser(jwt_str), token
        # 返回TUser、token
        return user, token
