# -*- coding: utf-8 -*-
"""
@File    : permissions.py
@Author  : 大五学长
@Time    : 2022/5/16 22:25
@desc    :
         
"""
import logging
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response

from api.authentication import AnonymousUser
from api.models import TUser

debugger = logging.getLogger('debugger')


class AuthenticatedUserPermission(BasePermission):
    """已认证的用户，包含实名认证和匿名认证"""
    def has_permission(self, request: Request, view):
        if isinstance(request.user, (TUser, AnonymousUser)):
            return True
        return False


class RealNameAuthenticatedUserPermission(BasePermission):
    """实名认证的用户"""
    def has_permission(self, request: Request, view):
        if isinstance(request.user, TUser):
            return True
        return False


class AnonymousAuthenticatedUserPermission(BasePermission):
    """匿名认证的用户"""
    def has_permission(self, request: Request, view):
        if isinstance(request.user, AnonymousUser):
            return True
        return False


class NotAuthenticatedUserPermission(BasePermission):
    """未认证用户"""
    def has_permission(self, request: Request, view):
        if request.auth is None:
            return True
        return False
