# -*- coding: utf-8 -*-
"""
路由、模板、菜单、子菜单
管理员界面：
    - 菜单管理： 添加菜单、删除菜单、修改菜单名称/顺序
    - 分组管理：
    -
"""
from django.urls import path
from .views import home
from .utils import bind_template

urlpatterns = [
    # home页面获取菜单
    path('home/', home.Home.as_view()),
    path('welcome/', bind_template('welcome.html')),
    # 用户管理
    path('login/', bind_template('login.html'), name='login'),
    path('user/password/change/', bind_template('user/change_my_password.html')),
    # 订单管理
    path('order/import/', bind_template('order/import.html')),
    path('order/export/', bind_template('order/export.html')),
    # 任务管理
    path('todos/tasks/', bind_template('todos/tasks.html')),
    path('todos/new_task/', bind_template('todos/new_task.html')),
    path('todos/labels/', bind_template('todos/labels.html')),
]
