from rbac import models
from django.conf import settings

def init_permission(request,uname):
    """
    权限注入函数
    :param request: request对象
    :param uname: 用户名称
    :return:
    """
    premission_list = models.Role.objects.filter(userinfo__username=uname).values(
        'permissions__id',
        'permissions__menu_id',
        'permissions__url',
        'permissions__title',
        'permissions__icon',
        'permissions__parent_id',
        'permissions__menu__title',
        'permissions__menu__weight',
        'permissions__menu__icon',
        'permissions__url_name',
    ).distinct()

    menu_dict ={}
    permission_dict = {}
    url_names = []

    for permission in premission_list:
        url_names.append(permission['permissions__url_name'])
        permission_dict[permission['permissions__id']] = permission
        if permission['permissions__menu_id']:
            if menu_dict.get(permission['permissions__menu_id']):
                menu_dict[permission['permissions__menu_id']]['children'].append(
                    {
                        'title':permission['permissions__title'],
                        'icon':permission['permissions__icon'],
                        'url':permission['permissions__url'],
                        'id':permission['permissions__id'],
                    }
                )
            else:
                menu_dict[permission['permissions__menu_id']] = {
                    'title':permission['permissions__menu__title'],
                    'icon':permission['permissions__menu__icon'],
                    'weight':permission['permissions__menu__weight'],
                    'children':[
                        {
                            'title': permission['permissions__title'],
                            'icon': permission['permissions__icon'],
                            'url': permission['permissions__url'],
                            'id': permission['permissions__id'],
                        }
                    ]
                }

    #校验用户是否有某个功能的权限，中间件中使用
    request.session[settings.PERMISSION_KEY] = permission_dict

    #生成左侧菜单用的
    request.session[settings.MENU_KEY] = menu_dict
    request.session['url_names'] = url_names