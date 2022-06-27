# -*- coding: utf-8 -*-
"""
功能：自定义管理后台
"""
from django.db import connection
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import SimpleTemplateResponse
from rest_framework.views import APIView

from api.authentication import UserAuthentication
from api.models import TUser


class Home(APIView):
    # permission_classes = [AuthenticatedUserPermission]
    # 匿名用户进入之后跳转登陆页面
    authentication_classes = [UserAuthentication]
    permission_classes = []

    def get(self, req: Request):
        """
        获取用户菜单详情
        """
        if not isinstance(req.user, TUser):
            return HttpResponseRedirect('/my-admin/login/')
        # 获取当前用户
        user = req.user
        uid = user.id
        #
        sql = """
                    SELECT
                        t_menu.title menu_title,
                        t_submenu.title title,
                        t_submenu.path path
                    FROM t_submenu LEFT JOIN t_menu ON t_menu.id=t_submenu.menu_id
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
        return render(req, 'home.html', context={'user_menus': user_menus})


class WelcomePage(APIView):
    def get(self, req: Request):
        return SimpleTemplateResponse(template='welcome.html')
