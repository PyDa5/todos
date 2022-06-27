# -*- coding:utf8 -*-
"""
功能：群管理模块
"""
import re

from django.db.models import Q
from django.http import QueryDict
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import TTeam, TTeamMember, TUser
from api.serializers import TeamCreateValidator, TeamProfileAdminSerializer, TeamSerializer, TeamProfileSerializer, \
    UserProfileSerializer


class TeamProfileAdminAPIView(APIView):
    """群资料管理，需要管理员权限"""

    def put(self, req: Request, team_id):
        """修改群资料"""
        cli_data: QueryDict = req.data.copy()
        cli_data.setdefault('team_id', team_id)
        print(team_id)
        # 校验数据
        serializer = TeamProfileAdminSerializer(data=cli_data)
        serializer.is_valid(raise_exception=True)
        teams = TTeam.objects.filter(
            Q(num=serializer.validated_data['num'], is_active=True)
            & (Q(admin=req.user.id) | Q(creator=req.user.id))
        )
        if not teams:
            return Response({'detail': '群不存在'})

        teams.update(**serializer.validated_data)
        return Response({'msg': '群资料修改成功'})


class TeamAdminAPIView(APIView):
    """需要管理员权限"""

    def delete(self, req: Request):
        """删除群聊"""
        team_id = req.query_params.get('team_id', None)
        if not team_id:
            return Response({'detail': 'team_id参数缺失'})

        if not re.compile(r'\d+').fullmatch(team_id):
            return Response({'detail': 'team_id参数有误'})

        team: TTeam = TTeam.objects.filter(id=team_id, creator=req.user.id, is_active=True).first()
        if not team:
            return Response({'detail': f'未找到该群'})

        team.is_active = False
        team.save()
        return Response({'msg': '团队已解散'})

    def post(self, req: Request):
        """创建群聊"""
        cli_data: QueryDict = req.data.copy()

        serializer = TeamCreateValidator(data=cli_data, context={'user': req.user})
        serializer.is_valid(raise_exception=True)
        new_team = serializer.save()
        data = {
            'id': new_team.id,
            'num': new_team.num
        }
        return Response(data=data)


class TeamMemberAdminAPIView(APIView):
    """群成员管理，需要管理员权限"""

    def post(self, req: Request, team_id, user_id):
        """邀请成员加入"""
        # 数据校验
        userid = user_id
        user_nickname = req.data.get('user_nickname', None)
        if not user_nickname:
            return Response({'detail': '参数user_nickname不能为空'})
        # 先判断自己属不属于该群
        is_member = TTeamMember.objects.filter(user_id=req.user.id, team_id=team_id, joined=True)
        if not is_member:
            return Response({'detail': '你不在该群中或群不存在'})
        # 再判断目标用户是否存在
        invited_user = TUser.objects.filter(id=userid, is_active=True).first()
        if not invited_user:
            return Response({'detail': '被邀请的用户不存在或未激活'})
        # 接着判断用户是否已经在群里面
        member = TTeamMember.objects.filter(team_id=team_id, user_id=userid).first()
        if member:
            if not member.joined:
                member.joined = True
                member.save()
                return Response({'msg': '已同意加群'})
            return Response({'detail': '当前用户已加入'})
        else:
            # 将用户加入到群成员表中
            TTeamMember.objects.create(
                user_nickname=user_nickname,
                team_memo=None,
                team_id=team_id,
                user_id=userid,
                joined=True
            )
            return Response({'msg': '邀请加群成功'})

    def delete(self, req: Request, team_id, user_id):
        """删除群成员，当自己是管理员或者创建人，且踢的时候不是踢自己，则操作成功"""
        # 数据校验
        userid = user_id
        member = TTeamMember.objects.filter(
            Q(user_id=userid, team_id=team_id, joined=True) &
            ~Q(user_id__in=[userid, ]) &
            (Q(team__creator=req.user.id) | Q(team__admin=req.user.id))
        )
        if not member:
            return Response({'detail': '未找到满足条件的成员'})
        member.delete()
        return Response({'msg': '踢出成功'})


class TeamProfileAPIView(APIView):
    """获取群资料"""

    def get(self, req: Request, team_id):
        team = TTeam.objects.filter(id=team_id).first()
        serializer = TeamProfileSerializer(instance=team)
        return Response({'data': serializer.data})


class TeamMemberListAPIView(APIView):
    """获取群成员列表"""

    def get(self, req: Request, team_id):
        # 取出team的成员列表
        team_ids = TTeamMember.objects.filter(user_id=req.user.id, team_id=team_id, joined=True).values_list('team_id')
        user_ids = TTeamMember.objects.filter(team_id__in=team_ids).values_list('user_id')
        users = TUser.objects.filter(Q(id__in=user_ids)).all()
        serializer = UserProfileSerializer(instance=users, many=True)
        return Response({'data': serializer.data})


class MyTeamListAPIView(APIView):
    """
    获取我加入的所有群信息
    返回字段：
        team_id: 群ID
        num: 群号
        name: 群名称
        desc: 群描述
        logo: 群logo
        user_nickname: 用户昵称
        memo: 群别称
    """

    def get(self, req: Request):
        team_ids = TTeamMember.objects.filter(user_id=req.user.id).values_list('team_id')
        teams = TTeam.objects.filter(id__in=team_ids).all()
        print(teams)
        serializer = TeamSerializer(instance=teams, many=True)
        return Response({'data': serializer.data})


class WithdrawAPIView(APIView):
    def delete(self, req: Request, team_id):
        """退出团队"""
        ret = TTeamMember.objects.filter(team_id=team_id, user_id=req.user.id, joined=True).update(joined=False)
        if not ret:
            return Response({'detail': '用户不在群中'})
        return Response({'msg': '退群成功'})
