# -*- coding: utf-8 -*-
"""
@File    : caches.py
@Author  : 大五学长
@Time    : 2022/5/15 19:56
@desc    :
         
"""
import logging
import random
from abc import abstractmethod
from rest_framework.request import Request

from django.core.cache import cache

from api.models import TUser

debugger = logging.getLogger('debugger')

CACHE_KEY_CAPTCHA_REGISTER = 'captcha:register:{email}'


def generate_captcha():
    """6位数字验证码"""
    first_number = str(random.randint(1, 9))
    other_numbers = ''.join([str(random.randint(0, 9)) for i in range(5)])
    return first_number + other_numbers


class BaseCaptchaCache(object):
    pattern = None
    cache_max_age = 1*60

    def __new__(cls, *args, **kwargs):
        if cls.pattern is None:
            return NotImplemented('未设定缓存pattern')
        return super().__new__(cls)

    def __init__(self, request: Request):
        super().__init__()
        self.request = request
        self.cache_key = self.pattern.format(token=self.request.auth)

    @abstractmethod
    def cache_captcha(self, request: Request, *args, **kwargs):
        pass

    @abstractmethod
    def read_captcha(self, request: Request, *args, **kwargs):
        pass

    @abstractmethod
    def remove_cache_captcha(self: Request, request, *args, **kwargs):
        pass


class RegisterCaptchaCache:
    pattern = 'captcha:register:{token}:{email}'

    def cache_captcha(self, token, email, max_age=60*1):
        """根据客户端token缓存注册验证码"""
        cache_key = self.pattern.format(token=token, email=email)
        captcha = generate_captcha()
        cache.set(cache_key, captcha, max_age)
        return captcha

    def read_captcha(self, token, email):
        """根据token读取验证码"""
        cache_key = self.pattern.format(token=token, email=email)
        return cache.get(cache_key, None)

    def remove_cache_captcha(self, token, email):
        cache_key = self.pattern.format(token=token, email=email)
        cache.delete(cache_key)


class ResetMyPasswordCaptchaCache(BaseCaptchaCache):
    """发送重置密码验证码"""
    pattern = 'captcha:reset_pwd:{token}'

    def cache_captcha(self, *args, **kwargs):
        captcha = generate_captcha()
        cache.set(self.cache_key, captcha, self.cache_max_age)
        print(captcha)
        return captcha

    def read_captcha(self, *args, **kwargs):
        print(self.cache_key)
        return cache.get(self.cache_key, None)

    def remove_cache_captcha(self, *args, **kwargs):
        cache.delete(self.cache_key)


class AnonymousUserEmailCache:
    pattern = 'anonymous:email:{token}'

    def set(self, request: Request, *args, **kwargs):
        self.cache(self.cache_key, self.pattern, )

    def get(self, request: Request, *args, **kwargs):
        pass

    def remove(self: Request, request, *args, **kwargs):
        pass


class UserIdCache:
    pattern = 'token:uid:{token}'
    max_age = 1*60

    def __init__(self, request):
        self.request = request
        self.cache_key = self.pattern.format(token=request.auth)

    def set(self, user: TUser):
        cache.set(self.cache_key, user.id)

    def get(self):
        return cache.get(self.cache_key, None)

    def remove(self):
        cache.delete(self.cache_key)
