# -*- coding: utf-8 -*-
"""
@File    : menu.py
@Author  : 大五学长
@Time    : 2022/5/17 23:33
@desc    : 查询用户菜单
"""
import logging

from django.db import connection
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from api.authentication import UserAuthentication, AnonymousUser
from api.permissions import AuthenticatedUserPermission

debugger = logging.getLogger('debugger')


class MyMenuAPIView(APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = [AuthenticatedUserPermission]

    def get(self, req: Request):
        """
        获取用户菜单
        用户菜单=个人菜单+所属分组菜单的集合
        菜单格式：
        """
        # 获取当前用户
        user = req.user
        uid = user.id
        #
        sql = """
            SELECT
                t_menu.title menu_title,
                t_submenu.title title,
                t_submenu.path path
            FROM t_submenu 
            LEFT JOIN t_menu ON t_menu.id=t_submenu.menu_id
            WHERE t_submenu.id IN (
                SELECT t_user_submenu.submenu_id submenu_id FROM t_user_submenu
                WHERE t_user_submenu.user_id = %s
                UNION
                SELECT t_group_submenu.submenu_id submenu_id  FROM t_group_submenu
                WHERE t_group_submenu.group_id IN (
                    SELECT t_user_groups.group_id group_id FROM t_user_groups WHERE user_id = %s
                )
            )
        """
        user_menus = {}
        with connection.cursor() as cursor:
            cursor.execute(sql, (uid, uid))
            columns = [row[0] for row in cursor.description]
            submenus = [dict(zip(columns, row)) for row in cursor]
            for submenu in submenus:
                menu_title = submenu['menu_title']
                if menu_title not in user_menus:
                    user_menus[submenu['menu_title']] = []
                user_menus[submenu['menu_title']].append({
                    'title': submenu['title'],
                    'path': submenu['path']
                })
        print(user_menus)
        return Response({'data': user_menus})
