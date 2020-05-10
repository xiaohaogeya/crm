from django.shortcuts import render,redirect,HttpResponse
from django.views import View
from django.forms import modelformset_factory,formset_factory
from django.db.models import Q
from rbac import models
from app01.models import UserInfo
from rbac import myforms
from rbac.serve import routes

# Create your views here.


#角色展示
class RoleView(View):
    def get(self,request):
        role_lists = models.Role.objects.all()
        return render(request,'rbac/role_list.html',{'role_lists':role_lists})

#角色添加或修改
class Role_Add_EditView(View):
    def get(self,request,rid = None):
        role_objs = models.Role.objects.filter(id = rid).first()
        form = myforms.RoleModelForm(instance=role_objs)
        return render(request,'rbac/role_add.html',{'form':form})

    def post(self,request,rid = None):
        role_objs = models.Role.objects.filter(id=rid).first()
        form = myforms.RoleModelForm(request.POST,instance=role_objs)
        if form.is_valid():
            form.save()
            return redirect('rbac:role_list')
        else:
            return render(request,'rbac/role_add.html',{'form':form})

#删除角色
def role_del(request,rid):
    models.Role.objects.filter(id=rid).delete()
    return redirect('rbac:role_list')


#菜单展示
class MenuView(View):
    def get(self,request):
        menu_lists = models.Menu.objects.all()
        mid = request.GET.get('mid')
        if mid:
            permissions_list = models.Permission.objects.filter(Q(menu_id=mid)|Q(parent__menu_id=mid)).values()
        else:
            permissions_list = models.Permission.objects.all().values()



        permissions_dict = {}
        # print(permissions_list)
        for permissions in permissions_list:
            mid = permissions.get('menu_id')
            if mid:
                permissions_dict[permissions['id']] = permissions
                permissions_dict[permissions['id']]['children'] = []

        for node in permissions_list:
            pid = node.get('parent_id')
            if pid:
                permissions_dict[pid]['children'].append(node)

        return render(request,'rbac/menu_list.html',{'menu_lists':menu_lists,'permissions_list':permissions_list,'mid':mid})

#菜单添加或编辑
class Menu_Add_EditView(View):
    def get(self,request,mid=None):
        menu_obj = models.Menu.objects.filter(id=mid).first()
        form = myforms.MenuModelForm(instance=menu_obj)
        return render(request,'rbac/menu_add.html',{'form':form})

    def post(self,request,mid=None):
        menu_obj = models.Menu.objects.filter(id=mid).first()
        form = myforms.MenuModelForm(request.POST,instance=menu_obj)
        if form.is_valid():
            form.save()
            return redirect('rbac:menu_list')
        else:
            return render(request,'rbac/menu_add.html',{'form':form})


#权限删除
def menu_del(request,mid):
    models.Menu.objects.filter(id=mid).delete()
    return redirect('rbac:menu_list')

#权限添加或编辑
class Permission_Add_EditView(View):
    def get(self,request,pid=None):
        permission_obj = models.Permission.objects.filter(id=pid).first()
        form = myforms.PermissionModelForm(instance=permission_obj)
        return render(request,'rbac/permission_add.html',{'form':form})

    def post(self,request,pid=None):
        permission_obj = models.Permission.objects.filter(id=pid).first()
        form = myforms.PermissionModelForm(request.POST,instance=permission_obj)
        if form.is_valid():
            form.save()
            return redirect('rbac:menu_list')
        else:
            return render(request, 'rbac/permission_add.html', {'form': form})

#批量操作权限
def multi_permissions(request):
    # print(1111111111111111111111)
    post_type = request.GET.get('type')
    # print(post_type)
    # 权限更新和编辑
    Formset = modelformset_factory(models.Permission, myforms.MultiPermissionModelForm, extra=0)
    # 权限添加
    AddFormset = formset_factory(myforms.MultiPermissionModelForm, extra=0)
    # 获取数据库中现有的所有权限数据
    permissions = models.Permission.objects.all()
    # 获取项目的路由系统中所有的URL
    router_dict = routes.get_all_url_dict(ignore_namespace_list=['admin', ])
    # 数据库中所有权限的别名
    permissions_name_set = set([i.url_name for i in permissions])
    # 路由系统中所有的权限的别名
    router_name_set = set(router_dict.keys())

    if request.method == "POST" and post_type == 'add':
        add_formset = AddFormset(request.POST)
        if add_formset.is_valid():
            permission_obj_list = [models.Permission(**i) for i in add_formset.cleaned_data]
            # print(permission_obj_list)
            query_list = models.Permission.objects.bulk_create(permission_obj_list)
            for i in query_list:
                permissions_name_set.add(i.url_name)

    # 要新增的别名
    add_name_set = router_name_set - permissions_name_set
    add_formset = AddFormset(initial=[row for name, row in router_dict.items() if name in add_name_set])
    # print(add_formset)
    # 要删除的别名
    del_name_set = permissions_name_set - router_name_set
    del_formset = Formset(queryset=models.Permission.objects.filter(url_name__in=del_name_set))
    # 要更新的别名
    update_name_set = permissions_name_set & router_name_set
    update_formset = Formset(queryset=models.Permission.objects.filter(url_name__in=update_name_set))




    if request.method == "POST" and post_type == "update":
        update_formset = Formset(request.POST)
        if update_formset.is_valid():
            update_formset.save()
            update_formset = Formset(queryset=models.Permission.objects.filter(url_name__in=update_name_set))

    if request.method == "POST" and post_type == "delete":
        del_formset = Formset(request.POST)
        if del_formset.is_valid():
            del_formset.clean()
            del_formset = Formset(queryset=models.Permission.objects.filter(url_name__in=del_name_set))


    return render(request, 'rbac/multi_permissions.html',{
        'del_formset':del_formset,
        'update_formset':update_formset,
        'add_formset':add_formset,
        'cho':1,
    })


#权限分配
def distribute_permissions(request):
    uid = request.GET.get('uid')
    rid = request.GET.get('rid')
    postType = request.POST.get('postType')
    # print(uid,'uid')
    # print(rid,'rid')
    # print(postType,'postType')
    #用户
    if request.method == "POST" and postType == "role":
        user = UserInfo.objects.filter(id = uid).first()
        if not user:
            return HttpResponse('该用户不存在')
        user.roles.set(request.POST.getlist('roles'))
    #角色
    if request.method == "POST" and postType == "permission" and rid:
        role = models.Role.objects.filter(id=rid).first()
        if not role:
            return HttpResponse('该角色不存在')
        role.permissions.set(request.POST.getlist('permissions'))

    #所有用户
    user_list = UserInfo.objects.all()
    #用户对应的角色
    user_has_roles = UserInfo.objects.filter(id= uid).values('id','roles')
    user_has_roles_dict = {item['roles']:None for item in user_has_roles}
    #所有角色
    role_list = models.Role.objects.all()
    if rid:
        role_has_permissions = models.Role.objects.filter(id=rid).values('id','permissions')
    elif uid and not rid:
        user = UserInfo.objects.filter(id=uid).first()
        if not user:
            return HttpResponse('用户不存在')
        role_has_permissions = user.roles.values('id','permissions')
    else:
        role_has_permissions = []

    role_has_permissions_dict = {item['permissions']:None for item in role_has_permissions}
    all_menu_list =[]
    #一级菜单
    queryset = models.Menu.objects.values('id','title')
    menu_dict = {}
    for item in queryset:
        item['children'] = [] #放二级菜单，父权限
        menu_dict[item['id']] = item #如menu_dict = {'一级菜单id':{'id':'一级菜单id','title':'一级菜单名称','children':[]},...}
        all_menu_list.append(item)

    other = {'id':None,'title':'其他','children':[]}
    all_menu_list.append(other)
    menu_dict[None] = other
    #二级菜单
    root_permission = models.Permission.objects.filter(menu__isnull=False).values('id','title','menu_id')
    root_permission_dict = {}
    for per in root_permission:#per字典,model对象,per = {'id':'二级菜单id','title':'二级菜单名称','menu_id':'对应的一级菜单id'}...
        per['children'] = [] #放子权限，如添加、删除、编辑
        nid = per['id'] #二级菜单权限id
        menu_id = per['menu_id'] #一级菜单权限id
        root_permission_dict[nid] = per #如root_permission_dict = {'二级菜单id':{'id':'二级菜单id','title':'二级菜单名称','menu_id':'对应的一级菜单id','children':[]},...}
        menu_dict[menu_id]['children'].append(per) #将per添加到menu_dict，即一级菜单的字典的每一个children中,即menu_dict的数据结构变成：
        #menu_dict = {'一级菜单id':{'id':'一级菜单id','title':'一级菜单名称','children':[{'id':'二级菜单id','title':'二级菜单名称','menu_id':'对应的一级菜单id'},...]},...}


    #二级菜单子权限
    node_permission = models.Permission.objects.filter(menu__isnull=True).values('id','title','parent_id')
    for per in node_permission:#per字典,model对象,per = {'id':'二级菜单包括子权限id','title':'二级菜单包括子权限名称','parent_id':'id'}...
        pid = per['parent_id']
        if not pid:
            menu_dict[None]['children'].append(per)
            continue
        root_permission_dict[pid]['children'].append(per) #将per添加到二级菜单的字典的children中,即menu_dict变成如下数据结构：
        #menu_dict = {'一级菜单id':
        # {'id':'一级菜单id','title':'一级菜单名称','children':[{
        # 'id':'二级菜单id','title':'二级菜单名称','menu_id':'对应的一级菜单id','children':[{
        # 'id':'二级菜单包括子权限id','title':'二级菜单包括子权限名称','parent_id':'id'}，...]},...]},...}
        #每次循环都会自动添加到menu_dict中，因为字典是可变数据类型

    return render(
        request,
        'rbac/distribute_permissions.html',
        {
            'user_list':user_list,
            'role_list':role_list,
            'user_has_roles_dict':user_has_roles_dict,
            'role_has_permissions_dict':role_has_permissions_dict,
            'all_menu_list':all_menu_list,
            'uid':uid,
            'rid':rid,
            'cho':1,
        }
    )


#权限删除
def permissions_del(request,pid):
    models.Permission.objects.filter(id=pid).delete()
    return redirect('rbac:multi_permissions')