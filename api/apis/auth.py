# -*- coding: utf-8 -*-
"""
@File    : views.py
@Author  : 大五学长
@Time    : 2022/5/16 17:14
@desc    :
访问/api/auth/接口
    - 无username、password，则颁发匿名token
    - 有username、password，账密正确则颁发已认证token，错误则颁发匿名token
    - 若客户端请求头携带
"""
import datetime
import logging

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.token import generate_auth_token, generate_anonymous_token, decrypt_client_jwt
from api.models import TUser

debugger = logging.getLogger('debugger')


class AuthAPIView(APIView):
    permission_classes = []

    def post(self, req: Request):
        """
        获取认证用户token
        Request params:
            username: 用户名
            password: 密码
        """
        # 若客户端存在未过期token，则无需再次登陆
        cli_token = req.COOKIES.get('token', None)
        if cli_token:
            payload = decrypt_client_jwt(cli_token)
            exp = int(payload.get('exp', None))
            current_timestamp = int(datetime.datetime.timestamp(datetime.datetime.now()))
            if exp > current_timestamp and 'uid' in payload:
                return Response({'msg': '用户已登录'})
        #
        cli_data = req.data
        if 'username' not in cli_data:
            return Response({'msg': 'username必填'})
        if 'password' not in cli_data:
            return Response({'msg': 'password必填'})

        user: TUser = TUser.objects.get_user(username=cli_data['username'])

        if not user:
            server_token, client_token = generate_anonymous_token()
            rsp = Response({'msg': '用户不存在'})
            rsp.set_cookie('token', client_token)
            return rsp

        if not user.validate_password(cli_password=cli_data['password']):
            server_token, client_token = generate_anonymous_token()
            rsp = Response({'msg': '密码错误'})
            rsp.set_cookie('token', client_token)
            return rsp

        server_token, client_token = generate_auth_token(user)
        rsp = Response({'msg': '登陆成功'})
        rsp.set_cookie('token', client_token)
        rsp.headers['Authorization'] = f'Token {client_token}'
        return rsp

    def get(self, req: Request):
        """GET获取匿名token"""
        server_token, client_token = generate_anonymous_token()
        rsp = Response({
            'msg': '用户未认证',
            'url': '/api/auth/',
            'method': 'POST',
            'content-type': 'application/json',
            'fields': ['username', 'password'],
            'public_key': 'xxxx',
            'public_key_encode': 'base64'
        })
        rsp.set_cookie('token', client_token)
        return rsp
