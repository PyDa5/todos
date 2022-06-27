# -*- coding: utf-8 -*-
"""
@File    : todos.py
@Author  : 大五学长
@Time    : 2022/5/22 21:13
@desc    :
    - 创建TODO
    - 修改TODO状态
    - 删除TODO
    - 查询TODO详情
    - 获取TODO列表[（待处理、处理中、已完成、暂搁置）,（标签x, all）]
"""
import json
import logging
import time

from django.db import connections, connection, IntegrityError, transaction
from django.db.models import Q, F, RestrictedError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import TTodos, TTodoLabel, TUserPreference
from api.permissions import RealNameAuthenticatedUserPermission
from api.serializers import MyTodoSerializer, MyTodoStatusTransformValidator, MyTodoLabelModifyValidator, \
    MyTodoLabelsSerializer, MyRemarkSerializer, MyTodoListValidator

debugger = logging.getLogger('debugger')


class MyTodoAPIView(APIView):
    permission_classes = [RealNameAuthenticatedUserPermission]

    def post(self, req: Request):
        """创建TODO"""
        cli_data = req.data.copy()
        cli_data['user_id'] = req.user.id
        serializer = MyTodoSerializer(data=cli_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': '创建成功', 'data': serializer.validated_data})

    def delete(self, req: Request):
        """删除TODO"""
        pk = req.data.get('id', None)
        if not pk:
            return Response({'detail': '缺少参数id'}, status=400)
        sql = """
        DELETE FROM t_todos
        WHERE id = %s AND user_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(sql, (pk, req.user.id))
        return Response({'msg': '操作成功'})

    def get(self, req: Request):
        """获取一个TODO的详情
        is_active = True
        """
        pk = req.query_params.get('id', None)
        user_id = req.user.id
        if not pk:
            return Response({'detail': '缺少参数id'})
        fields = [
            "user_id",
            "username",
            "status_id",
            "status_name",
            "label_id",
            "label_name",
            "content",
            "create_time",
            "parent_id",
            "root_id",
            "team_id"
        ]
        sql = """
        SELECT 
            t_todos.id id, 
            t_todos.user_id user_id, 
            t_user.username username, 
            t_todos.status_id status_id, 
            t_todo_status.name status_name, 
            t_todos.label_id label_id, 
            t_todo_label.label_name label_name, 
            t_todos.content content, 
            t_todos.create_time create_time,
            t_todos.parent_id parent_id, 
            t_todos.root_id root_id,
            t_todos.team_id team_id
        FROM t_todos
        LEFT JOIN t_user ON t_user.id = t_todos.user_id
        LEFT JOIN t_todo_status ON t_todo_status.id = t_todos.status_id
        LEFT JOIN t_todo_label ON t_todo_label.id = t_todos.label_id
        WHERE t_todos.user_id = %s AND t_todos.id = %s AND t_todos.is_active = 1
        ORDER BY t_todos.create_time DESC
        """
        data = []
        with connection.cursor() as cursor:
            cursor.execute(sql, (user_id, pk))
            for row in cursor:
                data.append(dict(zip(fields, row)))
        return Response({'data': data})

    def put(self, req: Request):
        """修改TODO状态"""
        cli_data = req.data
        serializer = MyTodoStatusTransformValidator(data=cli_data)
        serializer.is_valid(raise_exception=True)
        clean_data = serializer.validated_data

        todo = TTodos.objects.filter(id=clean_data['id'], user_id=req.user.id).first()
        if not todo:
            return Response({'detail': '记录不存在'})
        # 更新数据
        status_id = cli_data['status_id']
        affect_rows = TTodos.objects.filter(
            Q(id=clean_data['id']) & ~Q(status_id__in=[status_id])
        ).update(status_id=status_id)
        if affect_rows != 0:
            return Response({'msg': '操作成功'})
        return Response({'msg': '操作失败'}, status=400)


class MyTodoListAPIView(APIView):
    permission_classes = [RealNameAuthenticatedUserPermission]

    def get(self, req: Request):
        """获取TODO列表"""
        data = []
        serializer = MyTodoListValidator(data=req.query_params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        # 从请求获取user_id、status_id
        user_id = req.user.id

        # 设置需要返回客户端的字段
        fields = [
            "id",
            "user_id",
            "username",
            "status_id",
            "status_name",
            "label_id",
            "label_name",
            "content",
            "create_time",
            "parent_id",
            "root_id",
            "team_id",
        ]
        # 拼串查询
        sql_body = """
            SELECT 
                t_todos.id id, 
                t_todos.user_id user_id, 
                t_user.username username, 
                t_todos.status_id status_id, 
                t_todo_status.name status_name, 
                t_todos.label_id label_id, 
                t_todo_label.label_name label_name, 
                t_todos.content content, 
                t_todos.create_time create_time,
                t_todos.parent_id parent_id, 
                t_todos.root_id root_id,
                t_todos.team_id team_id
            FROM t_todos
            LEFT JOIN t_user ON t_user.id = t_todos.user_id
            LEFT JOIN t_todo_status ON t_todo_status.id = t_todos.status_id
            LEFT JOIN t_todo_label ON t_todo_label.id = t_todos.label_id
            WHERE t_todos.user_id = %s AND t_todos.is_active = 1 
        """
        sql_order_by = " ORDER BY t_todos.create_time DESC"
        # SQL WHERE子句
        query_args = [user_id]
        if 'status_id' in validated_data:
            sql_body += ' AND t_todos.status_id = %s'
            query_args.append(validated_data.get('status_id'))
        if 'label_id' in validated_data:
            sql_body += ' AND t_todos.label_id = %s'
            query_args.append(validated_data.get('label_id'))
        if 'team_id' in validated_data:
            sql_body += ' AND t_todos.team_id = %s'
            query_args.append(validated_data.get('team_id'))
        if 'keyword' in validated_data:
            sql_body += ' AND t_todos.content LIKE %s'

            query_args.append(f'%{validated_data.get("keyword")}%')
        # SQL 分页查询
        sql_limit = ' '
        if 'page' in validated_data and 'page_size' in validated_data:
            # 限制查询数量
            page_index = validated_data['page'] - 1
            page_size = min(100, validated_data['page_size'])
            offset = page_index * page_size
            # sqlite3 查询语法
            sql_limit += f'LIMIT {page_size} OFFSET {offset}'

        # SQL语句
        sql = sql_body + sql_order_by + sql_limit
        # 执行并返回数据
        with connection.cursor() as cursor:
            cursor.execute(sql, query_args)
            for row in cursor:
                data.append(dict(zip(fields, row)))
        return Response({'data': data})


class MyTodoLabelAPIView(APIView):
    permission_classes = [RealNameAuthenticatedUserPermission]

    def post(self, req: Request):
        """创建标签"""
        label_name = req.data.get('label_name', None)
        if not label_name:
            return Response({'detail': '缺少参数label_name'}, status=400)
        user_id = req.user.id
        label_index = int(time.time())
        try:
            affect_rows = TTodoLabel.objects.create(
                user_id=user_id,
                label_name=label_name,
                label_index=label_index
            )
        except IntegrityError:
            return Response({'detail': '当前标签已存在'}, status=400)

        if affect_rows != 0:
            return Response({'msg': '创建成功'})
        return Response({'detail': '创建失败'}, status=500)

    def delete(self, req: Request):
        """删除标签"""
        pk = req.data.get('id', None)
        print(req.data)
        if not pk:
            return Response({'detail': '缺少参数id'}, status=400)
        instance = TTodoLabel.objects.filter(id=pk, user_id=req.user.id).first()
        if not instance:
            return Response({'detail': '标签不存在'}, status=400)
        try:
            instance.delete()
        except RestrictedError:
            return Response({'detail': '标签已被使用，无法删除'}, status=400)
        return Response({'msg': '操作成功'})

    def put(self, req: Request):
        """修改标签名称和顺序"""
        # 获取客户端表单
        cli_data = req.data
        # 数据校验
        serializer = MyTodoLabelModifyValidator(data=cli_data)
        serializer.is_valid(raise_exception=True)
        # 清洗后的数据
        clean_data = serializer.validated_data
        # 先判断源标签是否存在
        src_label = TTodoLabel.objects.filter(
            id=clean_data['id'],
            user_id=req.user.id,
        ).first()
        if not src_label:
            return Response({'detail': '标签不存在'}, status=400)
        try:
            with transaction.atomic():
                if 'label_index' in clean_data:
                    # 大于等于目标label_index的都自增1
                    TTodoLabel.objects.filter(
                        user_id=req.user.id,
                        label_index__gte=clean_data['label_index']
                    ).update(label_index=F('label_index') + 1)
                    src_label.label_index = clean_data['label_index']
                    src_label.save()
                if 'label_name' in clean_data:
                    src_label.label_name = clean_data['label_name']
                    src_label.save()
        except IntegrityError:
            return Response({'detail': '标签名称重复'}, status=400)
        return Response({'msg': '操作成功'})


class MyTodoLabelListAPIView(APIView):
    permission_classes = [RealNameAuthenticatedUserPermission]

    def get(self, req: Request):
        """获取标签列表"""
        labels = TTodoLabel.objects.filter(user_id=req.user.id).order_by('label_index').all()
        serializer = MyTodoLabelsSerializer(instance=labels, many=True)
        return Response({'data': serializer.data})


class TodoRemarkListAPIView(APIView):
    permission_classes = [RealNameAuthenticatedUserPermission]

    def get(self, req: Request):
        cli_data = req.query_params
        root_id: str = cli_data.get('root_id', None)
        if not root_id:
            return Response({'detail': '缺少参数root_id'})
        if not root_id.strip():
            return Response({'detail': 'root_id须为整数'})
        fields = [
            'id',
            "user_id",
            "username",
            "status_id",
            "status_name",
            "label_id",
            "label_name",
            "content",
            "create_time",
            "parent_id",
            "root_id"
        ]
        sql = """
            SELECT 
                    t_todos.id id, 
                    t_todos.user_id user_id, 
                    t_user.username username, 
                    t_todos.status_id status_id, 
                    t_todo_status.name status_name, 
                    t_todos.label_id label_id, 
                    t_todo_label.label_name label_name, 
                    t_todos.content content, 
                    t_todos.create_time create_time,
                    t_todos.parent_id parent_id, 
                    t_todos.root_id root_id
                FROM t_todos
                LEFT JOIN t_user ON t_user.id = t_todos.user_id
                LEFT JOIN t_todo_status ON t_todo_status.id = t_todos.status_id
                LEFT JOIN t_todo_label ON t_todo_label.id = t_todos.label_id
            WHERE t_todos.is_active = 1 AND (t_todos.id = %s OR t_todos.root_id = %s )
            ORDER BY t_todos.id DESC 
        """
        data = []
        with connection.cursor() as cursor:
            cursor.execute(sql, (root_id, root_id))
            for row in cursor:
                data.append(dict(zip(fields, row)))
        return Response({'data': data})

    def post(self, req: Request):
        """创建新TODO"""
        cli_data = req.data.copy()
        cli_data['user_id'] = req.user.id
        serializer = MyRemarkSerializer(data=cli_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'msg': '创建成功', 'data': serializer.validated_data})


class MyTodoStyleAPIView(APIView):
    permission_classes = [RealNameAuthenticatedUserPermission]

    def post(self, req: Request):
        """切换TODO展示方式"""
        user_id = req.user.id
        preference_key = 'todo-show-style'
        cli_data = req.data
        if 'type' not in cli_data:
            return Response({'detail': '缺少参数type'}, status=400)
        typ = cli_data['type']
        if typ in ['card', 'table']:
            preference = TUserPreference.objects.filter(user_id=user_id, key=preference_key).first()
            if preference:
                preference.value = typ
                preference.save()
            else:
                TUserPreference.objects.create(
                    user_id=user_id,
                    key=preference_key,
                    value='card'
                )
            return Response({'msg': '操作成功'})
        else:
            return Response({'detail': 'type参数取值错误'}, status=400)

    def get(self, req: Request):
        user_id = req.user.id
        preference_key = 'todo-show-style'
        instance = TUserPreference.objects.filter(user_id=user_id, key=preference_key).first()
        if not instance:
            return Response({'data': 'table'})
        return Response({'data': instance.value})