# -*- coding: utf-8 -*-
"""
@File    : celery.py
@Author  : 大五学长
@Time    : 2022/5/16 9:52
@desc    :
         
"""
from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# 指定Django默认配置文件模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diamond.settings')

# 为我们的项目myproject创建一个Celery实例。这里不指定broker backend 容易出现错误。
# 如果没有密码 使用 'redis://127.0.0.1:6379/0'
app = Celery(
    'untitled',
    broker='redis://:password@127.0.0.1:6379/0',
    backend='redis://:password@127.0.0.1:6379/0')


# 这里指定从django的settings.py里读取celery配置
app.config_from_object('django.conf:settings')
# 下面的设置就是关于调度器beat的设置,
# 具体参考https://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html
app.conf.beat_schedule = {
    'autosc': {  # 取个名字
        'task': 'user.tasks.auto_sc',  # 设置是要将哪个任务进行定时
        'schedule': crontab(),  # 调用crontab进行具体时间的定义
    },
}
# 自动从所有已注册的django app中加载任务
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)