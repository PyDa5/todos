from django.core.management.base import BaseCommand
from django.conf import settings

from api.models import TMenu, TSubMenu, TGroup, TGroupSubmenu


class UserMenus:
    """创建用户菜单"""
    def __init__(self, menu_config):
        self.menu_config = menu_config

        self._group_default: TGroup = None
        self.menus: dict = {}
        self.submenus: dict = {}

    def add_menu(self, title):
        """添加菜单"""
        menu: TMenu = TMenu.objects.filter(title=title).first()
        if not menu:
            self.menus[title] = TMenu.objects.create(title=title)
        else:
            self.menus[title] = menu
        print(f'- {title}')
        return self.menus[title]

    def add_submenu(self, menu: TMenu, title: str, path: str, join_to_default_group=False):
        """添加子菜单"""
        submenu: TSubMenu = TSubMenu.objects.filter(menu_id=menu.id, title=title).first()
        if not submenu:
            self.submenus[title] = TSubMenu.objects.create(menu_id=menu.id, title=title, path=path)
        else:
            submenu.path = path
            submenu.save()
            self.submenus[title] = submenu
        if join_to_default_group:
            self.add_group_submenu(self._group_default, self.submenus[title])
            print(f'  - {title} (default)')
        else:
            print(f'  - {title}')
        return self.submenus[title]

    def add_group_submenu(self, group: TGroup, submenu: TSubMenu):
        group_submenu: TGroupSubmenu = TGroupSubmenu.objects.filter(group_id=group.id, submenu_id=submenu.id).first()
        if not group_submenu:
            group_submenu = TGroupSubmenu.objects.create(group_id=group.id, submenu_id=submenu.id)
        return group_submenu

    def _add_default_group(self):
        """配置default用户组"""
        group_default: TGroup = TGroup.objects.filter(name='default').first()
        if not group_default:
            self._group_default = TGroup.objects.create(name='default')
        else:
            self._group_default = group_default
        return self._group_default

    def migrate(self):
        self._add_default_group()
        for menu_title in self.menu_config:
            menu = self.add_menu(menu_title)
            submenus = self.menu_config[menu_title]
            for submenu_title in submenus:
                self.add_submenu(menu, submenu_title, *submenus[submenu_title])


class Command(BaseCommand):
    def handle(self, *args, **options):
        menus = settings.MENUS
        UserMenus(menus).migrate()
