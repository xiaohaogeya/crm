import re
from rbac import models
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect,render,HttpResponse
from django.urls import reverse

class Auth(MiddlewareMixin):

    def process_request(self,request):

        # 登录认证白名单
        white_list = [reverse('login'),reverse('register'),'/admin/.*']
        # 登录认证

        # 权限认证白名单
        white_permission_list = ['/rbac/multi/permissions/','/rbac/distribute/permissions/']


        bread_crumb = [
            {'title':'首页','url':reverse('home')},


        ]

        request.pid = None


        current_path = request.path
        for i in white_list:
            if re.match(i,current_path):
                break
        else:
            is_login = request.session.get('name')
            if not is_login:
                return redirect('/login/')

            else:

                for purl in white_permission_list:
                    # print(purl)
                    if re.match(purl,current_path):

                        return
                else:

                    # 权限认证
                    permission_dict = request.session.get(settings.PERMISSION_KEY)

                    # re.match('/customer/edit/(?P<cid>\d+)/',customer/edit/2/)
                    #/customer/edit/(?P<cid>\d+)/  -- customer/edit/2/
                    for permission in permission_dict.values(): #[{'url':'/custer/'}]
                        # if current_path == permission['permissions__url']:
                        reg = r'^%s$'%permission['permissions__url']
                        if re.match(reg,current_path):  #/customer/add/
                            pid = permission['permissions__parent_id'] #None

                            if pid:
                                # obj = models.Permission.objects.filter(id=pid).first()
                                parent_dict = permission_dict[str(pid)]
                                # 添加二级菜单
                                bread_crumb.append({
                                    'title': parent_dict['permissions__title'],
                                    'url': parent_dict['permissions__url'],
                                })

                                # 添加子权限
                                bread_crumb.append({
                                    'title': permission['permissions__title'],
                                    'url': permission['permissions__url'],
                                })

                                # bread_crumb = [
                                #     {'title': '首页', 'url': 'javascript:void(0);'},
                                #     {'title': '客户展示', 'url': 'javascript:void(0);'},
                                #     {'title': '客户添加', 'url': 'javascript:void(0);'},
                                #
                                # ]

                                request.pid = pid  #wsgihttprequest对象



                            else:
                                if permission['permissions__url'] != reverse('home'):

                                    bread_crumb.append({
                                        'title':permission['permissions__title'],
                                        'url':permission['permissions__url'],
                                    })
                                request.pid = permission['permissions__id']

                            request.session['bread_crumb'] = bread_crumb
                            return
                    else:
                        return HttpResponse('您不配!!!')







