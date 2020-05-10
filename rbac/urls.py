from django.conf.urls import url,include
from rbac import views

urlpatterns = [
    #角色展示
    url(r'^role/list/',views.RoleView.as_view(),name='role_list'),
    #角色添加
    url(r'^role/add/',views.Role_Add_EditView.as_view(),name='role_add'),
    #角色编辑
    url(r'^role/edit/(\d+)/',views.Role_Add_EditView.as_view(),name='role_edit'),
    #角色删除
    url(r'^role/del/(\d+)/',views.role_del,name='role_del'),


    #菜单展示
    url(r'^menu/list/',views.MenuView.as_view(),name='menu_list'),
    #菜单添加
    url(r'^menu/add/',views.Menu_Add_EditView.as_view(),name='menu_add'),
    #菜单编辑
    url(r'^menu/edit/(\d+)/',views.Menu_Add_EditView.as_view(),name='menu_edit'),
    #菜单删除
    url(r'^menu/del/(\d+)/',views.menu_del,name='menu_del'),

    #权限添加
    url(r'^permission/add/',views.Permission_Add_EditView.as_view(),name='permission_add'),

    #批量操作
    url(r'^multi/permissions/',views.multi_permissions,name='multi_permissions'),
    #权限分配
    url(r'^distribute/permissions/',views.distribute_permissions,name='distribute_permissions'),
    #权限删除
    url(r'^permissions/del/',views.permissions_del,name='permissions_del'),


]