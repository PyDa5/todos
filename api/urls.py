# -*- coding: utf-8 -*-
from django.urls import path, re_path
from .apis import user, auth, menu, todos, teams

urlpatterns = [
    # 认证
    path('auth/', auth.AuthAPIView.as_view()),
    # 用户模块
    path('user/register/', user.RegisterAPIView.as_view()),
    path('user/login/', user.LoginAPIView.as_view()),
    path('user/logout/', user.LogoutAPIView.as_view(), name='logout'),
    path('user/reset_password/', user.ResetMyPasswordAPIView.as_view()),
    path('user/change_password/', user.ChangeMyPasswordAPIView.as_view()),
    path('user/username/', user.WhoAmIAPIView.as_view()),
    # 菜单模块
    path('menus/', menu.MyMenuAPIView.as_view()),
    # TODOS
    path(r'todos/', todos.MyTodoAPIView.as_view()),
    path(r'todos/list/', todos.MyTodoListAPIView.as_view()),
    path(r'todos/labels/', todos.MyTodoLabelAPIView.as_view()),
    path(r'todos/labels/list/', todos.MyTodoLabelListAPIView.as_view()),
    path(r'todos/remarks/', todos.TodoRemarkListAPIView.as_view()),
    path(r'todos/preference/style/', todos.MyTodoStyleAPIView.as_view()),
    # 验证码模块
    path('captcha/register/', user.RegisterCaptchaAPIView.as_view()),
    path('captcha/reset_password/', user.ResetMyPasswordCaptchaAPIView.as_view()),
    # 群TODO管理
    re_path(r'teams/$', teams.TeamAdminAPIView.as_view()),
    re_path(r'teams/list/$', teams.MyTeamListAPIView.as_view()),
    re_path(r'teams/(?P<team_id>\d+)/$', teams.WithdrawAPIView.as_view()),
    re_path(r'teams/(?P<team_id>\d+)/admin/members/(?P<user_id>\d+)/$', teams.TeamMemberAdminAPIView.as_view()),
    re_path(r'teams/(?P<team_id>\d+)/admin/profile/$', teams.TeamProfileAdminAPIView.as_view()),
    re_path(r'teams/(?P<team_id>\d+)/members/list/$', teams.TeamMemberListAPIView.as_view()),
    re_path(r'teams/(?P<team_id>\d+)/profile/$', teams.TeamProfileAPIView.as_view()),
]
