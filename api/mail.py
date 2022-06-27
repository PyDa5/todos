# -*- coding: utf-8 -*-
"""
@File    : mail.py
@Author  : 大五学长
@Time    : 2022/5/17 16:27
@desc    :
         
"""
import logging

from django.core.mail import send_mail as django_send_mail
from django.conf import settings as django_settings

debugger = logging.getLogger('debugger')


def send_captcha_mail(subject: str, message: str, recipient_list: list, typ, user):
    cache_key = 'captcha:{typ}:{}'
    django_send_mail(
        subject=subject,
        message=message,
        from_email=django_settings.EMAIL_FROM,
        recipient_list=recipient_list
    )


def get_cache_captcha():
    """获取缓存的验证码"""
    pass
