# -*- coding: utf-8 -*-
"""
@File    : manager.py
@Author  : 大五学长
@Time    : 2022/5/15 18:47
@desc    :
         
"""
import logging
import hashlib
from django.db import models

debugger = logging.getLogger('debugger')


class UserManager(models.Manager):
    def create_user(self, username: str,  email, password: str):
        """sha256存储用户密码"""
        sha256_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        user = self.create(
            username=username,
            password=sha256_password,
            email=email
        )
        return user

    def get_user(self, username):
        # sha256_cli_password = hashlib.sha256(cli_password.encode('utf-8')).hexdigest()
        return self.filter(username=username).first()
