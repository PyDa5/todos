# -*- coding: utf-8 -*-
import datetime
import logging

from django.conf import settings as django_settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import IntegrityError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentication import UserAuthentication, AnonymousUser
from api.caches import RegisterCaptchaCache, ResetMyPasswordCaptchaCache, UserIdCache
from api.models import TUser
from api.permissions import AnonymousAuthenticatedUserPermission
from api.response import AnonymousUserResponse
from api.serializers import RegisterFormSerializer, EmailSerializer, LoginFormSerializer, \
    ResetMyPasswordValidator, ChangeMyPasswordSerializer
from api.token import generate_anonymous_token, decrypt_client_jwt, generate_auth_token

logger = logging.getLogger('debugger')
registerCaptchaCache = RegisterCaptchaCache()


class RegisterAPIView(APIView):
    """用户注册
    """
    # 需要提供有效token才能访问
    permission_classes = []

    def post(self, req: Request):
        """
        Request params:
            username: 用户名
            password: 密码
            email: 邮箱
            captcha: 验证码
        """
        data = req.data
        # 校验数据
        serializer = RegisterFormSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        clean_data = serializer.validated_data
        print(clean_data)
        # 校验token
        cli_jwt = req.COOKIES.get('token', None)
        if not cli_jwt:
            return Response({'detail': '未提供token'})
        payload = decrypt_client_jwt(cli_jwt)
        token = payload.get('token', None)
        if token is None:
            return Response({'detail': 'token无效'})
        server_captcha = registerCaptchaCache.read_captcha(token, clean_data['email'])
        # 验证码过期
        if server_captcha is None:
            return Response({'detail': '验证码已过期'})
        # 验证码有误
        if clean_data['captcha'] != server_captcha:
            return Response({'detail': '验证码不正确'})
        # 注册用户
        try:
            serializer.save()
        except IntegrityError:
            registerCaptchaCache.remove_cache_captcha(token, clean_data['email'])
            return Response({'detail': '当前用户已被注册'})
        except Exception as e:
            raise e
        return Response({'msg': '注册成功'})


class RegisterCaptchaAPIView(APIView):
    permission_classes = []

    def post(self, req: Request):
        """
        发送注册验证码
        Request params:
            email: 1174446068@qq.com
        """
        if 'email' not in req.data:
            return Response({'detail': '未提供email地址'})
        serializer = EmailSerializer(data=req.data)
        serializer.is_valid(raise_exception=True)
        clean_data = serializer.validated_data
        # from .caches import RegisterCaptchaCache
        jwt_token = req.COOKIES.get('token')
        payload = decrypt_client_jwt(jwt_token)
        token = payload.get('token', generate_anonymous_token()[1])
        captcha = registerCaptchaCache.cache_captcha(token, clean_data['email'])
        # celery异步发送短信
        send_mail(
            'MyAdmin注册验证码',
            captcha,
            from_email=django_settings.EMAIL_FROM,
            recipient_list=[clean_data['email']]
        )
        # 给客户端颁发token，用于查询验证码
        rsp = Response({'msg': '验证码已发送'})
        return rsp


class LoginAPIView(APIView):
    """用户登陆"""
    # 登陆接口无需登陆后才能访问
    permission_classes = []

    def post(self, req: Request):
        """
        Request params:
            username: xxx
            password: 123456
        """
        # 若用户已登录，则无需再次登陆
        cli_token = req.COOKIES.get('token', None)
        if cli_token:
            payload = decrypt_client_jwt(cli_token)
            exp = payload.get('exp', None)
            if exp is not None:
                exp = int(exp)
                current_timestamp = int(datetime.datetime.timestamp(datetime.datetime.now()))
                if exp > current_timestamp and 'uid' in payload:
                    return Response({'msg': '用户已登录'})
        cli_data = req.data
        # 校验数据
        serializer = LoginFormSerializer(data=cli_data)
        serializer.is_valid(raise_exception=True)
        clean_data = serializer.validated_data
        # 查找用户
        user: TUser = TUser.objects.get_user(username=clean_data['username'])
        # 用户不存在
        if not user:
            return Response({'detail': '用户不存在'})
        # 密码错误
        if not user.validate_password(clean_data['password']):
            return Response({'detail': '密码错误'})
        # ban token
        # token expire_time
        server_token, client_token = generate_auth_token(user)
        rsp = Response({'msg': '登陆成功'})
        rsp.set_cookie('token', client_token)
        return rsp


class ResetMyPasswordAPIView(APIView):
    permission_classes = [AnonymousAuthenticatedUserPermission]

    def post(self, req: Request):
        """
        重置密码
        Request params:
            email: 邮箱
            captcha: 验证码
            new_password: 新密码
        """
        cli_data = req.data
        # 表单校验
        serializer = ResetMyPasswordValidator(data=cli_data)
        serializer.is_valid(raise_exception=True)
        clean_data = serializer.validated_data
        # 验证码校验
        captcha_cache = ResetMyPasswordCaptchaCache(request=req)
        cached_captcha = captcha_cache.read_captcha()
        print(cached_captcha)
        cli_captcha = clean_data['captcha']
        if cached_captcha is None:
            return Response({'detail': '验证码已过期'}, status=400)
        if cli_captcha != cached_captcha:
            captcha_cache.remove_cache_captcha()
            return Response({'detail': '验证码错误'}, status=400)
        # 缓存读取token对应的用户ID
        uid_cache = UserIdCache(request=req)
        uid = uid_cache.get()
        if not uid:
            return Response({'detail': '验证码已过期'}, status=400)

        user: TUser = TUser.objects.filter(id=uid).first()
        if not user:
            return Response({'detail': '用户不存在'}, status=400)
        uid_cache.remove()
        ret = user.change_password(new_password=clean_data['new_pwd1'])
        print(ret)
        return Response({'msg': '密码重置成功'})


class ResetMyPasswordCaptchaAPIView(APIView):
    permission_classes = [AnonymousAuthenticatedUserPermission]

    def post(self, req: Request):
        """发送重置密码的邮件"""
        print(req.auth, req.user)
        if isinstance(req.user, TUser):
            return Response({'detail': '已登录用户不允许此操作'}, status=400)
        cli_data = req.data
        # 表单校验
        if 'email' not in cli_data:
            return Response({'detail': '缺少email字段'}, status=400)
        email = cli_data.get('email')
        # 根据email查找用户
        user: TUser = TUser.objects.filter(email=email).first()
        if not user:
            return Response({'detail': '用户不存在'}, status=400)
        captcha_cache = ResetMyPasswordCaptchaCache(request=req)
        captcha = captcha_cache.cache_captcha()
        # 缓存当前token对应的用户ID
        uid_cache = UserIdCache(request=req)
        uid_cache.set(user)
        # 发送邮件
        send_mail(
            'MyAdmin密码重置',
            f'验证码为{captcha}，如非本人操作，请忽略！',
            from_email=django_settings.EMAIL_FROM,
            recipient_list=[email, ]
        )
        return Response({'msg': '验证码已发送至邮箱'})


class WhoAmIAPIView(APIView):
    def get(self, req: Request):
        return Response({'data': req.user.username})


class LogoutAPIView(APIView):
    permission_classes = []

    def get(self, req: Request):
        # 清除会话数据
        # 清除客户端cookie
        user = req.user
        if isinstance(user, AnonymousUser):
            return Response({'detail': '用户未登陆'}, status=400)
        rsp = Response({'msg': '成功退出'})
        # 删除客户端token
        rsp.delete_cookie('token')
        return rsp


class MyMenuAPIView(APIView):
    authentication_classes = [UserAuthentication]

    def get(self, req: Request):
        """获取我的菜单"""
        user = req.user
        if isinstance(user, AnonymousUser):
            return Response({})


class ChangeMyPasswordAPIView(APIView):
    def post(self, req: Request):
        data = req.data
        # 表单校验
        serializer = ChangeMyPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        clean_data = serializer.validated_data
        # 先判断用户新密码和原密码是否一致
        if clean_data['old_pwd'] == clean_data['new_pwd1'] == clean_data['new_pwd2']:
            return Response({'detail': '原密码和新密码相同，修改不成功'}, status=400)
        # 获取当前用户
        user: TUser = req.user
        if not user.validate_password(clean_data['old_pwd']):
            return Response({'detail': '原密码有误输入'}, status=400)
        if serializer.validated_data['new_pwd1'] != serializer.validated_data['new_pwd2']:
            return Response({'detail': '新密码两次输入不一致'}, status=400)
        # 修改密码
        user.change_password(new_password=clean_data['new_pwd1'])
        return Response({'msg': '密码修改成功'})
