# -*- coding: utf-8 -*-
"""
@File    : utils.py
@Author  : 大五学长
@Time    : 2022/5/18 22:11
@desc    :
         
"""
import logging

from django.http import HttpResponseRedirect
from rest_framework.request import Request
from rest_framework.response import SimpleTemplateResponse
from rest_framework.views import APIView

from api.authentication import UserAuthentication, AnonymousUser
from api.models import TUser
from api.permissions import AuthenticatedUserPermission, RealNameAuthenticatedUserPermission

debugger = logging.getLogger('debugger')


def bind_template(template: str):
    if not template.endswith('.html'):
        template += '.html'

    class MyAPIView(APIView):
        permission_classes = [AuthenticatedUserPermission]
        # 匿名用户进入之后跳转登陆页面
        authentication_classes = [UserAuthentication]
        permission_classes = []

        def get(self, req: Request):
            """
            获取用户菜单详情
            """
            login_path = '/my-admin/login/'
            # print(isinstance(req.user, RealName), req.user, type(req.user), req.path != login_path)
            if not isinstance(req.user, TUser) and req.path != login_path:
                return HttpResponseRedirect(login_path)
            return SimpleTemplateResponse(template)

    return MyAPIView.as_view()
