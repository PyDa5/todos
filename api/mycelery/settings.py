# -*- coding: utf-8 -*-
"""
@File    : settings.py
@Author  : 大五学长
@Time    : 2022/5/16 9:48
@desc    :
         
"""
from django.conf import settings as django_settings
# celery相关配置
# 配置celery时区，默认时UTC。
timezone = django_settings.TIME_ZONE

# 任务队列的链接地址 celery配置redis作为broker。redis有16个数据库，编号0~15，这里使用第1个。
broker_url = 'redis://127.0.0.1:6379/1'

# 设置存储结果的后台  结果队列的链接地址
result_backend = 'redis://127.0.0.1:6379/15'

# 可接受的内容格式
accept_content = ["json"]
# 任务序列化数据格式
task_serializer = "json"
# 结果序列化数据格式
result_serializer = "json"

# 可选参数：给某个任务限流
# task_annotations = {'tasks.my_task': {'rate_limit': '10/s'}}

# 可选参数：给任务设置超时时间。超时立即中止worker
task_time_limit = 10 * 60

# 可选参数：给任务设置软超时时间，超时抛出Exception
# task_soft_time_limit = 10 * 60

# 可选参数：如果使用django_celery_beat进行定时任务
# beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"

# 更多选项见
# https://docs.celeryproject.org/en/stable/userguide/configuration.html
