import hashlib

from django.db import models

from api.manager import UserManager


class TUser(models.Model):
    """用户表"""
    id = models.AutoField(
        primary_key=True,
        db_column='id',
        help_text='ID'
    )
    username = models.CharField(
        max_length=150,
        null=False,
        unique=True,
        db_column='username',
        help_text='用户名'
    )
    password = models.CharField(
        max_length=128,
        null=False,
        db_column='password',
        help_text='密码'
    )
    email = models.EmailField(
        max_length=254,
        null=False,
        unique=True,
        db_column='email',
        help_text='邮箱'
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        db_column='phone_number',
        help_text='手机号'
    )
    first_name = models.CharField(
        max_length=150,
        null=False,
        db_column='first_name',
        help_text='first name'
    )
    last_name = models.CharField(
        max_length=150,
        null=False,
        db_column='last_name',
        help_text='last name'
    )
    is_superuser = models.BooleanField(
        default=False,
        db_column='is_superuser',
        help_text='是否超级管理员'
    )
    is_staff = models.BooleanField(
        default=False,
        db_column='is_staff',
        help_text='是否内部员工'
    )
    is_active = models.BooleanField(
        default=True,
        db_column='is_active',
        help_text='是否启用账户'
    )
    date_joined = models.DateTimeField(
        auto_now_add=True,
        db_column='date_joined',
        help_text='加入日期'
    )
    last_login = models.DateTimeField(
        null=True,
        db_column='last_login',
        help_text='上次登陆日期'
    )

    class Meta:
        managed = True
        db_table = 't_user'

    objects = UserManager()

    @property
    def perms(self):
        """用户权限清单"""
        pass

    def has_perms(self, perms):
        pass

    def validate_password(self, cli_password: str):
        """将客户端密码sha256后，和库中密码比对"""
        sha256_cli_password = hashlib.sha256(cli_password.encode('utf-8')).hexdigest()
        return self.password == sha256_cli_password

    def change_password(self, new_password: str):
        """修改用户密码"""
        sha256_password = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
        self.password = sha256_password
        self.save()


class TGroup(models.Model):
    """分组表"""
    id = models.AutoField(
        primary_key=True,
        help_text='ID'
    )
    name = models.CharField(
        max_length=150,
        null=False,
        db_column='name',
        help_text='组名'
    )

    class Meta:
        managed = True
        db_table = 't_group'


class TMenu(models.Model):
    id = models.IntegerField(
        primary_key=True,
        auto_created=True,
        db_column='id',
        help_text='菜单ID'
    )
    title = models.CharField(
        max_length=10,
        null=True,
        db_column='title',
        unique=True,
        help_text='菜单标题'
    )

    class Meta:
        managed = True
        db_table = 't_menu'
        verbose_name_plural = '添加主菜单'

    def __str__(self):
        return self.title


class TIFrameSrc(models.Model):
    path = models.CharField(
        max_length=255,
        primary_key=True,
        db_column='path',
        unique=True,
        help_text='IFrame路由'
    )
    desc = models.CharField(
        max_length=50,
        null=False,
        db_column='desc',
        help_text='URL地址说明'
    )

    class Meta:
        managed = True
        db_table = 't_iframe_src'
        verbose_name_plural = '路由表'

    def __str__(self):
        return f'{self.desc}({self.path})'


class TSubMenu(models.Model):
    id = models.AutoField(
        primary_key=True,
        help_text='子菜单ID'
    )
    title = models.CharField(
        max_length=10,
        db_column='title',
        null=False,
        help_text='子菜单标题'
    )
    path = models.CharField(
        max_length=255,
        db_column='path',
        null=False,
        help_text='子菜单路由'
    )
    menu = models.ForeignKey(
        TMenu,
        on_delete=models.CASCADE,
        db_column='menu_id',
        to_field='id',
        db_constraint=False  # 逻辑外键
    )

    class Meta:
        managed = True
        db_table = 't_submenu'
        verbose_name_plural = '添加子菜单'

    def __str__(self):
        return self.menu.title + '  >  ' + self.title


class TUserSubmenu(models.Model):
    """用户菜单表
    用于给指定用户单独开菜单权限
    """
    user = models.ForeignKey(
        TUser,
        on_delete=models.CASCADE,  # 用户删了，子菜单删掉
        null=False,
        db_column='user_id',
        db_constraint=False,
        help_text='用户ID'
    )
    submenu = models.ForeignKey(
        TSubMenu,
        on_delete=models.CASCADE,  # 子菜单删了，用户子菜单就没有了
        null=False,
        db_column='submenu_id',
        help_text='子菜单ID',
        db_constraint=False
    )

    class Meta:
        managed = True
        db_table = 't_user_submenu'
        verbose_name_plural = '设置个人菜单'

    def __str__(self):
        return self.submenu.title + '  >  ' + self.submenu.title


class TGroupSubmenu(models.Model):
    """分组子菜单表"""
    group = models.ForeignKey(
        TGroup,
        on_delete=models.RESTRICT,  # 被引用了就不能删
        db_column='group_id',
        to_field='id',
        help_text='分组ID',
        db_constraint=False  # 逻辑外键，数据库不生成外键
    )
    submenu = models.ForeignKey(
        TUserSubmenu,
        on_delete=models.RESTRICT,  # 被引用了就不能删
        db_column='submenu_id',
        help_text='子菜单ID',
        db_constraint=False  # 逻辑外键，数据库不生成外键
    )

    class Meta:
        managed = True
        db_table = 't_group_submenu'
        verbose_name_plural = '设置分组菜单'

    def __str__(self):
        return self.submenu.title + '  >  ' + self.submenu.title


class TContentType(models.Model):
    """模型视图类"""
    id = models.AutoField(
        primary_key=True,
        db_column='id',
        help_text='ID'
    )
    app_label = models.CharField(
        max_length=100,
        null=False,
        db_column='app_label',
        help_text='app_label'
    )
    model = models.CharField(
        max_length=100,
        null=False,
        db_column='model',
        help_text='视图或者数据库模型'
    )

    class Meta:
        managed = True
        db_table = 't_content_type'


class TPermission(models.Model):
    """权限表"""
    id = models.AutoField(
        primary_key=True,
        db_column='id',
        help_text='ID'
    )
    content_type = models.ForeignKey(
        TContentType,
        on_delete=models.CASCADE,
        db_column='content_type_id',
        db_constraint=False,
        help_text='模型或视图对象'
    )
    codename = models.CharField(
        max_length=100,
        null=False,
        db_column='codename',
        help_text='权限编码'
    )
    name = models.CharField(
        max_length=100,
        null=False,
        db_column='name',
        help_text='权限名称'
    )

    class Meta:
        managed = True
        db_table = 't_permission'


class TUserGroup(models.Model):
    """用户-用户组"""
    id = models.AutoField(
        primary_key=True,
        db_column='id',
        help_text='ID'
    )
    user = models.ForeignKey(
        TUser,
        on_delete=models.CASCADE,
        null=False,
        db_column='user_id',
        db_constraint=False,
        help_text='用户名'
    )
    group = models.ForeignKey(
        TGroup,
        on_delete=models.CASCADE,
        null=False,
        db_column='group_id',
        db_constraint=False,
        help_text='用户组'
    )

    class Meta:
        managed = True
        db_table = 't_user_groups'


class TUserUserPermission(models.Model):
    """用户权限"""
    id = models.AutoField(
        primary_key=True,
        db_column='id',
        help_text='ID'
    )
    user = models.ForeignKey(
        TUser,
        on_delete=models.CASCADE,
        null=False,
        db_column='user_id',
        db_constraint=False,
        help_text='用户ID'
    )

    class Meta:
        managed = True
        db_table = 't_user_user_permissions'


class TGroupPermission(models.Model):
    """组权限"""
    id = models.AutoField(
        primary_key=True,
        db_column='id',
        help_text='ID'
    )
    user = models.ForeignKey(
        TUser,
        on_delete=models.CASCADE,
        null=False,
        db_column='user_id',
        db_constraint=False,
        help_text='用户ID'
    )
    group = models.ForeignKey(
        TGroup,
        on_delete=models.CASCADE,
        null=False,
        db_column='group_id',
        db_constraint=False,
        help_text='分组ID'
    )

    class Meta:
        managed = True
        db_table = 't_group_permission'


class TSession(models.Model):
    """会话表"""
    id = models.AutoField(
        primary_key=True,
        db_column='id',
        help_text='ID'
    )
    session_key = models.CharField(
        max_length=40,
        null=False,
        db_column='session_key',
        help_text='会话Key'
    )
    session_data = models.TextField(
        null=False,
        db_column='session_data',
        help_text='会话数据'
    )

    class Meta:
        managed = True
        db_table = 't_session'


class TTodoStatus(models.Model):
    id = models.AutoField(
        primary_key=True
    )
    name = models.CharField(
        max_length=10,
        null=False,
        default=0,
        choices=(
            (1, '待处理'),
            (2, '处理中'),
            (3, '已完成'),
            (4, '暂搁置')
        ),
        help_text='状态名称'
    )

    class Meta:
        managed = True
        db_table = 't_todo_status'


class TTodoLabel(models.Model):
    id = models.AutoField(
        primary_key=True,
        db_column='ID'
    )
    user = models.ForeignKey(
        TUser,
        on_delete=models.RESTRICT,
        db_column='user_id',
        db_constraint=False,
        help_text='用户ID'
    )
    label_name = models.CharField(
        max_length=10,
        null=False,
        unique=True,
        db_column='label_name',
        help_text='标签名称'
    )
    label_index = models.IntegerField(
        null=False,
        db_column='label_index',
        help_text='标签索引'
    )

    class Meta:
        managed = True
        db_table = 't_todo_label'


class TTodos(models.Model):
    id = models.AutoField(
        primary_key=True,
    )
    user = models.ForeignKey(
        TUser,
        on_delete=models.RESTRICT,
        db_column='user_id',
        null=False,
        db_constraint=False,
        help_text='用户ID'
    )
    status = models.ForeignKey(
        TTodoStatus,
        on_delete=models.RESTRICT,
        db_column='status_id',
        db_constraint=False,
        help_text='Todo状态'
    )
    label = models.ForeignKey(
        TTodoLabel,
        on_delete=models.RESTRICT,
        db_column='label_id',
        db_constraint=False,
        help_text='Todo分类标签'
    )

    content = models.CharField(
        max_length=1000,
        null=False,
        db_column='content',
        help_text='内容'
    )
    create_time = models.DateTimeField(
        auto_now=True,
        db_column='create_time',
        help_text='创建时间'
    )
    is_active = models.BooleanField(
        default=False,
        db_column='is_active',
        help_text='是否删除'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        default=None,
        null=True,
        db_column='parent_id',
        db_constraint=False,
        help_text='父TodoID',
        related_name='todo_parent'
    )
    root = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        default=None,
        null=True,
        db_column='root_id',
        db_constraint=False,
        help_text='根TodoID',
        related_name='todo_root'
    )
    team = models.ForeignKey(
        TTodoLabel,
        on_delete=models.CASCADE,
        related_name='todos_team',
        db_constraint=False,
        db_column='team_id',
        null=True,
        help_text='团队ID'
    )

    class Meta:
        managed = True
        db_table = 't_todos'


class TUserPreference(models.Model):
    id = models.AutoField(
        primary_key=True,
        db_column='id',
        help_text='ID'
    )
    user = models.ForeignKey(
        TUser,
        on_delete=models.CASCADE,
        null=False,
        db_column='user_id',
        db_constraint=False,
        help_text='用户ID',
    )
    key = models.CharField(
        max_length=20,
        null=False,
        db_column='key',
        help_text='key'
    )
    value = models.CharField(
        max_length=20,
        null=False,
        db_column='value',
        help_text='value'
    )

    class Meta:
        managed = True
        db_table = 't_user_preferences'


class TTeam(models.Model):
    id = models.AutoField(
        db_column='id',
        primary_key=True
    )
    name = models.CharField(
        db_column='name',
        max_length=20,
        help_text='群名称',
        null=False
    )
    desc = models.CharField(
        db_column='desc',
        max_length=100,
        help_text='群介绍',
        null=True
    )
    logo = models.FileField(
        upload_to='team_logo',
        db_column='logo',
        help_text='logo',
        null=False
    )
    create_time = models.DateTimeField(
        db_column='create_time',
        help_text='创建时间',
        null=False,
        auto_created=True
    )
    is_active = models.BooleanField(
        db_column='is_active',
        help_text='伪删除',
        default=False,
    )
    admin = models.ForeignKey(
        TUser,
        on_delete=models.CASCADE,
        db_constraint=False,
        db_column='admin',
        null=False,
        related_name='team_user_admin',
        help_text='管理员'
    )
    creator = models.ForeignKey(
        TUser,
        on_delete=models.RESTRICT,
        db_constraint=False,
        db_column='creator',
        null=False,
        related_name='team_user_creator',
        help_text='创建人'
    )
    num = models.CharField(
        db_column='num',
        max_length=8,
        null=False,
        help_text='群号'
    )
    md5sum_logo = models.CharField(
        db_column='md5sum_logo',
        max_length=32,
        null=False,
        help_text='logoMD5'
    )

    class Meta:
        managed = False
        db_table = 't_team'


class TTeamMember(models.Model):
    id = models.AutoField(
        db_column='id',
        primary_key=True
    )
    user_nickname = models.CharField(
        db_column='user_nickname',
        max_length=20,
        null=True,
        help_text='成员昵称'
    )
    team_memo = models.CharField(
        db_column='team_memo',
        max_length=20,
        null=True,
        help_text='群备注'
    )
    team = models.ForeignKey(
        TTeam,
        on_delete=models.CASCADE,
        db_constraint=False,
        db_column='team_id',
        null=False,
        help_text='归属群'
    )
    user = models.ForeignKey(
        TUser,
        on_delete=models.RESTRICT,
        db_column='user_id',
        null=False,
        help_text='归属用户'
    )
    joined = models.BooleanField(
        default=False,
        help_text='是否已加入'
    )

    class Meta:
        managed = False
        db_table = 't_team_member'
