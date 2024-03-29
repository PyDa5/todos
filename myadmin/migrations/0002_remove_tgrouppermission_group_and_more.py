# Generated by Django 4.0.4 on 2022-05-22 12:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myadmin', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tgrouppermission',
            name='group',
        ),
        migrations.RemoveField(
            model_name='tgrouppermission',
            name='user',
        ),
        migrations.RemoveField(
            model_name='tgroupsubmenu',
            name='group',
        ),
        migrations.RemoveField(
            model_name='tgroupsubmenu',
            name='submenu',
        ),
        migrations.RemoveField(
            model_name='tpermission',
            name='content_type',
        ),
        migrations.DeleteModel(
            name='TSession',
        ),
        migrations.RemoveField(
            model_name='tsubmenu',
            name='menu',
        ),
        migrations.RemoveField(
            model_name='tsubmenu',
            name='path',
        ),
        migrations.RemoveField(
            model_name='tusergroup',
            name='group',
        ),
        migrations.RemoveField(
            model_name='tusergroup',
            name='user',
        ),
        migrations.RemoveField(
            model_name='tusersubmenu',
            name='submenu',
        ),
        migrations.RemoveField(
            model_name='tusersubmenu',
            name='user',
        ),
        migrations.RemoveField(
            model_name='tuseruserpermission',
            name='user',
        ),
        migrations.DeleteModel(
            name='TContentType',
        ),
        migrations.DeleteModel(
            name='TGroup',
        ),
        migrations.DeleteModel(
            name='TGroupPermission',
        ),
        migrations.DeleteModel(
            name='TGroupSubmenu',
        ),
        migrations.DeleteModel(
            name='TIFrameSrc',
        ),
        migrations.DeleteModel(
            name='TMenu',
        ),
        migrations.DeleteModel(
            name='TPermission',
        ),
        migrations.DeleteModel(
            name='TSubMenu',
        ),
        migrations.DeleteModel(
            name='TUser',
        ),
        migrations.DeleteModel(
            name='TUserGroup',
        ),
        migrations.DeleteModel(
            name='TUserSubmenu',
        ),
        migrations.DeleteModel(
            name='TUserUserPermission',
        ),
    ]
