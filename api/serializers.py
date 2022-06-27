# -*- coding: utf-8 -*-
"""
@File    : serializers.py
@Author  : 大五学长
@Time    : 2022/5/15 16:24
@desc    :
         
"""
import datetime
import logging
import time
import hashlib

import filetype
from django.db import transaction
from rest_framework import serializers

from .models import TUser, TTodos, TTodoLabel, TUserGroup, TTeam, TTeamMember

logger = logging.getLogger('debugger')


class RegisterFormSerializer(serializers.Serializer):
    username = serializers.CharField(
        min_length=2,
        max_length=150,
        error_messages={
            'min_length': '用户名长度不能少于2个字符',
            'max_length': '用户名长度不能大于150个字符'
        }
    )
    password = serializers.CharField(
        min_length=8,
        max_length=20,
        trim_whitespace=True,
        error_messages={
            'min_length': '密码长度不能少于8位',
            'max_length': '密码长度不能超过20位'
        }
    )
    email = serializers.EmailField()
    captcha = serializers.RegexField(r'\d{6}')

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        # from django.db import transaction
        with transaction.atomic():
            DEFAULT_GROUP_ID = 1
            user = TUser.objects.create_user(
                username=validated_data['username'],
                password=validated_data['password'],
                email=validated_data['email']
            )
            user_group = TUserGroup.objects.create(
                group_id=DEFAULT_GROUP_ID,
                user_id=user.id
            )
        return validated_data


class CaptchaSerializer(serializers.Serializer):
    captcha = serializers.RegexField(
        r'\d{6}',
        trim_whitespace=True
    )

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class EmailSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    email = serializers.EmailField()


class LoginFormSerializer(serializers.Serializer):
    username = serializers.CharField(
        min_length=2,
        max_length=150,
        trim_whitespace=True
    )
    password = serializers.CharField(
        min_length=8,
        max_length=20,
        trim_whitespace=True
    )

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class ResetMyPasswordValidator(serializers.Serializer):
    email = serializers.EmailField()
    captcha = serializers.RegexField(r'\d{6}')
    new_pwd1 = serializers.SlugField(
        min_length=8,
        max_length=20
    )
    new_pwd2 = serializers.SlugField(
        min_length=8,
        max_length=20
    )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, attrs):
        pwd1 = attrs.get('new_pwd1', None)
        pwd2 = attrs.get('new_pwd2', None)
        if None in [pwd1, pwd2]:
            raise serializers.ValidationError('new_pwd1、new_pwd2不能为空')
        if pwd1 != pwd2:
            raise serializers.ValidationError('新密码两次输入不一致')
        return attrs


class MyMenuSerializer(serializers.Serializer):
    """获取我的菜单"""

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class ChangeMyPasswordSerializer(serializers.Serializer):
    old_pwd = serializers.CharField(
        min_length=8,
        max_length=20,
        trim_whitespace=True
    )
    new_pwd1 = serializers.CharField(
        min_length=8,
        max_length=20,
        trim_whitespace=True
    )
    new_pwd2 = serializers.CharField(
        min_length=8,
        max_length=20,
        trim_whitespace=True
    )

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class MyTodoSerializer(serializers.Serializer):
    """"""
    user_id = serializers.IntegerField()
    # 默认处理中
    doing = 2
    status_id = serializers.IntegerField(default=doing)
    label_id = serializers.IntegerField()
    content = serializers.CharField(
        allow_null=False,
        trim_whitespace=True,
        max_length=1000
    )
    create_time = serializers.DateTimeField(default=datetime.datetime.now())
    is_active = serializers.BooleanField(default=True)
    parent_id = serializers.IntegerField(default=None)
    root_id = serializers.IntegerField(default=None)
    team_id = serializers.IntegerField(default=None)

    def validate_label_id(self, attr):
        label = TTodoLabel.objects.filter(id=attr).first()
        if not label:
            raise serializers.ValidationError(detail='label_id不存在', code=400)
        return attr

    def validate_team_id(self, attr):
        if attr is None:
            return attr
        team = TTeam.objects.filter(id=attr).first()
        if not team:
            raise serializers.ValidationError(detail='team_id不存在', code=400)
        return attr

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        instance = TTodos.objects.create(
            **validated_data
        )
        return instance


class MyRemarkSerializer(serializers.Serializer):
    """"""
    user_id = serializers.IntegerField()
    # 备注内容默认已完成
    done = 3
    status_id = serializers.IntegerField(default=done)
    label_id = serializers.IntegerField(required=False)
    content = serializers.CharField(
        allow_null=False,
        trim_whitespace=True,
        max_length=1000
    )
    create_time = serializers.DateTimeField(default=datetime.datetime.now())
    is_active = serializers.BooleanField(default=True)
    parent_id = serializers.IntegerField(required=False)
    root_id = serializers.IntegerField()

    def validate_label_id(self, attr):
        label = TTodoLabel.objects.filter(id=attr).first()
        if not label:
            raise serializers.ValidationError(detail='label_id不存在', code=400)
        return attr

    def validate(self, attrs):
        # 检查是否存在root_id
        todo = TTodos.objects.filter(id=attrs['root_id']).first()
        if not todo:
            raise serializers.ValidationError('todo不存在')
        attrs['parent_id'] = todo.id
        attrs['label_id'] = todo.label_id
        return attrs

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        instance = TTodos.objects.create(
            **validated_data
        )
        return instance


class MyTodoStatusTransformValidator(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)
    status_id = serializers.IntegerField()

    def validate_status_id(self, attr):
        valid_status_code = [2, 3, 4]
        if attr not in valid_status_code:
            raise serializers.ValidationError(detail=f'status_id有效值为{valid_status_code}')
        return attr

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class MyTodoLabelModifyValidator(serializers.Serializer):
    id = serializers.IntegerField(min_value=0)
    label_index = serializers.IntegerField(
        required=False,
        min_value=1
    )
    label_name = serializers.CharField(
        required=False,
        trim_whitespace=True,
        allow_null=False,
        min_length=2,
        max_length=10,
    )

    def validate(self, attrs):
        label_index = attrs.get('label_index', None)
        label_name = attrs.get('label_name', None)
        if label_index is None and label_name is None:
            raise serializers.ValidationError('label_index、label_name参数至少提供一项')
        return attrs

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class MyTodoLabelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TTodoLabel
        fields = ['id', 'label_name', 'label_index']


class MyTodoListValidator(serializers.Serializer):
    status_id = serializers.IntegerField(required=False)
    label_id = serializers.IntegerField(required=False)
    team_id = serializers.IntegerField(required=False)

    page_size = serializers.IntegerField(required=False, min_value=1)
    page = serializers.IntegerField(required=False, min_value=1)

    keyword = serializers.CharField(required=False, min_length=1, trim_whitespace=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class TeamCreateValidator(serializers.ModelSerializer):
    """创建群聊表单校验"""
    # 客户端传递过来的数据
    name = serializers.CharField(trim_whitespace=True, min_length=1, max_length=20)
    desc = serializers.CharField(trim_whitespace=True, max_length=100)
    logo = serializers.FileField(allow_empty_file=False)

    admin = serializers.HiddenField(default=None)
    creator = serializers.HiddenField(default=None)

    # 自动生成的字段
    create_time = serializers.DateTimeField(default=datetime.datetime.now())
    is_active = serializers.BooleanField(default=True)
    num = serializers.CharField(default=None)
    md5sum_logo = serializers.CharField(default=None)

    def validate_logo(self, attr):
        allowed_image_types = ['jpg', 'jpeg', 'png']
        allowed_max_length = 1024*1024*1
        # 验证图片类型
        file_type = filetype.guess(attr)
        if not file_type:
            raise serializers.ValidationError(f'logo只能为{"、".join(allowed_image_types)}格式')
        elif not any([file_type.is_extension(suffix) for suffix in allowed_image_types]):
            raise serializers.ValidationError(f'logo只能为{"、".join(allowed_image_types)}格式')
        else:
            pass
        # 验证图片大小
        if len(attr) > allowed_max_length:
            raise serializers.ValidationError('图片尺寸过大，不能超过{:.2f}M'.format(allowed_max_length/(1024*1024)))
        return attr

    def validate_num(self, attr):
        num = str(int(time.time()))[-8:]
        return num

    def validate(self, attrs):
        # 计算文件md5sum
        logo = attrs['logo']
        hasher = hashlib.md5()
        for chunk in logo.chunks():
            hasher.update(chunk)
        md5 = hasher.hexdigest()
        attrs['md5sum_logo'] = md5
        # 避免用户上传重复的文件
        a_team: TTeam = TTeam.objects.filter(md5sum_logo=md5).first()
        if a_team:
            attrs['logo'] = a_team.logo
        # 将当前用户设置为创建人和管理员
        user = self.context.get('user')
        attrs['admin'] = attrs['creator'] = user
        return attrs

    class Meta:
        model = TTeam
        fields = '__all__'


class TeamProfileAdminSerializer(serializers.ModelSerializer):
    team_id = serializers.RegexField(r'\d+', source='num')
    name = serializers.CharField(trim_whitespace=True, min_length=1, max_length=20)
    desc = serializers.CharField(trim_whitespace=True, max_length=100, allow_null=True)
    logo = serializers.FileField(allow_empty_file=False)
    md5sum_logo = serializers.CharField(default=None)

    def validate_logo(self, attr):
        allowed_image_types = ['jpg', 'jpeg', 'png']
        allowed_max_length = 1024*1024*1
        # 验证图片类型
        file_type = filetype.guess(attr)
        if not file_type:
            raise serializers.ValidationError(f'logo只能为{"、".join(allowed_image_types)}格式')
        elif not any([file_type.is_extension(suffix) for suffix in allowed_image_types]):
            raise serializers.ValidationError(f'logo只能为{"、".join(allowed_image_types)}格式')
        else:
            pass
        # 验证图片大小
        if len(attr) > allowed_max_length:
            raise serializers.ValidationError('图片尺寸过大，不能超过{:.2f}M'.format(allowed_max_length/(1024*1024)))
        return attr

    def validate(self, attrs):
        # 计算文件md5sum
        logo = attrs['logo']
        hasher = hashlib.md5()
        for chunk in logo.chunks():
            hasher.update(chunk)
        md5 = hasher.hexdigest()
        attrs['md5sum_logo'] = md5
        # 避免用户上传重复的文件
        a_team: TTeam = TTeam.objects.filter(md5sum_logo=md5).first()
        if a_team:
            attrs['logo'] = a_team.logo
        return attrs

    class Meta:
        model = TTeam
        fields = ['team_id', 'name', 'desc', 'logo', 'md5sum_logo']


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = TTeam
        fields = ['id', 'name', 'desc', 'logo']


class TeamProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TTeam
        fields = ['id', 'name', 'desc', 'logo', 'admin', 'creator']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TUser
        fields = ['id', 'username', 'email']
