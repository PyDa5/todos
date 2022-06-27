from django.contrib import admin
from api import models as my_models
"""
将用户菜单注册到管理后台
"""


@admin.register(my_models.TMenu)
class MenuAdmin(admin.ModelAdmin):
    fields = ['title']
    list_display = ['title']


@admin.register(my_models.TSubMenu)
class SubMenuAdmin(admin.ModelAdmin):
    fields = ['title', 'path', 'menu']
    list_display = ['title', 'path', 'menu']


@admin.register(my_models.TGroupSubmenu)
class GroupSubmenuAdmin(admin.ModelAdmin):
    fields = ['group', 'submenu']
    list_display = ['group', 'submenu']


@admin.register(my_models.TUserSubmenu)
class UserSubmenuAdmin(admin.ModelAdmin):
    # fields = ['user', 'submenu']
    list_display = ['user', 'submenu']
# admin.site.register(my_models.UserSubmenu)


@admin.register(my_models.TIFrameSrc)
class IFrameSrcAdmin(admin.ModelAdmin):
    fields = ['path', 'desc']
    list_display = ['path', 'desc']


# apps_index = ['IFrameSrc', 'Menu', 'SubMenu', 'GroupSubmenu', 'UserSubmenu']
