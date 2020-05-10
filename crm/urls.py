"""crm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:7j
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from app01 import views
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #登录
    url(r'^login/', views.Login.as_view(),name='login'),
    #注册
    url(r'^register/', views.Register.as_view(),name='register'),
    #首页
    url(r'^home/', views.Home.as_view(),name='home'),
    #公户管理
    url(r'^customers/', views.Customers.as_view(),name='customers'),
    #我的客户管理
    url(r'^mycustomers/', views.Customers.as_view(),name='mycustomers'),
    #添加客户
    url(r'^customersAdd/', views.Customers_add.as_view(),name='customer_add'),
    #编辑客户
    url(r'^customersEdit/(\d+)/', views.Customers_add.as_view(),name='customer_edit'),
    #删除客户
    url(r'^customer_del/(\d+)/', views.customer_del,name='customer_del'),
    #注销用户
    url(r'^logout/', views.logout,name='logout'),
    #跟进记录
    url(r'^consultRecords/', views.ConsultRecords.as_view(),name='consultRecords'),
    #添加跟进记录
    url(r'^consultrecord_add/', views.ConsultRecord_add.as_view(),name='consultrecord_add'),
    #编辑跟进记录
    url(r'^consultrecord_edit/(\d+)/', views.ConsultRecord_add.as_view(),name='consultrecord_edit'),
    #删除跟进记录
    url(r'^consultrecord_del/(\d+)/', views.consultrecord_del,name='consultrecord_del'),
    #报名记录
    url(r'^enrollments/', views.Enrollments.as_view(),name='enrollments'),
    #添加报名记录
    url(r'^enrollments_add/', views.Enrollments_add.as_view(),name='enrollments_add'),
    #编辑报名记录
    url(r'^enrollments_edit/(\d+)/', views.Enrollments_add.as_view(),name='enrollments_edit'),
    #删除报名记录
    url(r'^enrollment_del/(\d+)/', views.enrollment_del,name='enrollment_del'),
    #课程记录
    url(r'^courserecords/', views.CourserecordsView.as_view(),name='courserecords'),
    #添加课程记录
    url(r'^courserecord/add', views.Courserecords_add.as_view(),name='courserecord_add'),
    #编辑课程记录
    url(r'^courserecord/edit/(\d+)/', views.Courserecords_add.as_view(),name='courserecord_edit'),
    #删除课程记录
    url(r'^courserecord/del/(\d+)/', views.courserecord_del,name='courserecord_del'),
    #学习记录
    url(r'^studyrecords/', views.StudyRecordView.as_view(),name='studyrecords'),
    #rbac组件的路由分发
    url(r'^rbac/', include('rbac.urls',namespace='rbac')),

]
