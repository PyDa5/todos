# -*- coding: utf-8 -*-
"""
@File    : token.py
@Author  : 大五学长
@Time    : 2022/5/15 20:20
@desc    : 会话管理
         
"""
import datetime
import logging
import uuid

import jwt
from django.conf import settings as django_settings

# TOKEN全局配置
from api.models import TUser

TOKEN_SECRET_KEY = getattr(django_settings, 'TOKEN_SECRET_KEY', django_settings.SECRET_KEY)
TOKEN_ALGORITHM = getattr(django_settings, 'TOKEN_ALGORITHM', 'HS256')
TOKEN_MAX_AGE = getattr(django_settings, 'TOKEN_MAX_AGE', 7*24*60*60)

debugger = logging.getLogger('debugger')


# 创建token
def generate_anonymous_token():
    """用于标识用户的UUID，同时防止客户端伪造UUID"""
    server_token = uuid.uuid4().hex.replace('-', '')
    encoder = jwt.PyJWT()
    exp = datetime.datetime.now() + datetime.timedelta(seconds=TOKEN_MAX_AGE)
    client_token = encoder.encode(
        payload={
            'token': server_token,
            'exp': exp
        },
        key=TOKEN_SECRET_KEY,
        algorithm=TOKEN_ALGORITHM
    )
    return server_token, client_token


def generate_auth_token(user):
    """token+uid+过期时间"""
    server_token = uuid.uuid4().hex.replace('-', '')
    encoder = jwt.PyJWT()
    exp = datetime.datetime.now() + datetime.timedelta(seconds=TOKEN_MAX_AGE)
    client_token = encoder.encode(
        payload={
            'token': server_token,
            'uid': user.id,
            'exp': exp
        },
        key=TOKEN_SECRET_KEY,
        algorithm=TOKEN_ALGORITHM
    )
    return server_token, client_token


def decrypt_client_jwt(cli_jwt) -> dict:
    """
    解析客户端token
    :Returns
        token: token
        exp: 过期时间
        uid: 用户自增ID
    """
    decoder = jwt.PyJWT()
    try:
        payload: dict = decoder.decode(
            cli_jwt,
            key=TOKEN_SECRET_KEY,
            algorithms=TOKEN_ALGORITHM
        )
    except:
        return {}
    return payload


def get_user_from_token(token):
    user = None
    return user
