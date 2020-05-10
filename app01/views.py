import json

from django.shortcuts import render,redirect,HttpResponse
from django.views import View
from app01 import myforms
from utils import md5,pager
from app01 import models
from django.db.models import Q
from crm import settings
from django.urls import reverse
from django.db import transaction
from django.http import JsonResponse
from django.forms import modelformset_factory
from rbac.serve.permission_insert import init_permission

# Create your views here.


class Register(View):
    def get(self,request):
        form_obj = myforms.UserForm()
        return render(request, 'auth/register.html', {'form_obj':form_obj})
    def post(self,request):
        form_obj = myforms.UserForm(request.POST)
        if form_obj.is_valid():
            data = form_obj.cleaned_data
            data.pop('password_again')
            data['password'] = md5.set_md5(data['password'],data['username'])
            models.UserInfo.objects.create(
                **data
            )
            return redirect('login')
        else:
            return render(request, 'auth/register.html', {'form_obj':form_obj})

class Login(View):
    def get(self,request):
        return render(request, 'auth/login.html')
    def post(self,request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = models.UserInfo.objects.filter(username=username,password=md5.set_md5(password,username))
        if user_obj:
            request.session['name'] = username
            #注入权限
            init_permission(request,username)
            return redirect('home')
        else:
            return render(request, 'auth/login.html', {'error': '用户名或密码有误'})

class Home(View):
    def get(self,request):
        return render(request,'home.html')
    def post(self,request):
        request.session.flush()
        print("已注销")
        return redirect('login')


#客户信息展示
class Customers(View):

    def get(self,request):
        path = request.path #请求路径，如/customers/
        current_page_num = request.GET.get('page') #当前页面数
        get_data = request.GET.copy()
        action = request.GET.get('action')
        kw = request.GET.get('kw')

        if path == reverse('customers'):
            gs = 1
            all_customers = models.Customer.objects.filter(delete_status=False,consultant__isnull=True).order_by('-id')
        else:
            gs = 2
            all_customers = models.Customer.objects.filter\
                (delete_status=False, consultant__username=request.session['name']).order_by('-id')
        if kw and action:
            q = Q()
            q.children.append([action,kw])
            all_customers = all_customers.filter(q)
        all_num_count = all_customers.count() #所有数据量
        page_obj = pager.Pagination(current_page_num,all_num_count,get_data,settings.PAGE_NUM_SHOW,
                                    settings.DATA_SHOW_NUMBER)
        page_html = page_obj.html()
        all_customers = all_customers[page_obj.start_data_num:page_obj.end_data_num]
        return render(request,'sales/customers_list.html',{'all_customers':all_customers,'page_html':page_html,'gs':gs})

    def post(self,request):
        bulk_action = request.POST.get('bulk_aciton') #批量操作
        cids = request.POST.getlist('cids') #客户id值
        if hasattr(self,bulk_action):
            ret = getattr(self,bulk_action)(request,cids)
            if ret:
                return ret
            else:
                return redirect('customers')
        else:
            return HttpResponse('你的操作有误')


    def reverse_gs(self,request,cids):

        with transaction.atomic(): #开启事务
            customers = models.Customer.objects.select_for_update().filter(id__in=cids) #select_for_update()开启锁
            msg_list = []
            for cus in customers:
                if cus.consultant:  #已经被拿走的客户
                    msg_list.append(cus.name)
            msg = ','.join(msg_list) + '这几个客户已经被拿走了'
            models.Customer.objects.filter(id__in=cids,consultant__isnull=True).update(
                consultant = models.UserInfo.objects.filter(username=request.session.get('name')).first()
            )
        if msg_list:
            return HttpResponse(msg)
        else:
            return redirect('customers')

    def reverse_sg(self,request,cids):
        models.Customer.objects.filter(id__in=cids).update(
            consultant = None
        )
        return redirect('mycustomers')

#添加或修改客户
class Customers_add(View):
    def get(self,request,cid = None):
        obj_list = models.Customer.objects.filter(id=cid).first()
        form_obj = myforms.CustomerModelForm(instance=obj_list)
        return render(request,'sales/customer_add.html',{'form_obj':form_obj,'cid':cid})

    def post(self,request,cid = None):
        next_url = request.GET.get('next')
        obj_list = models.Customer.objects.filter(id=cid).first()
        form_obj = myforms.CustomerModelForm(request.POST,instance=obj_list)
        if form_obj.is_valid():
            form_obj.save()
            if cid:
                return redirect(next_url)
            else:
                return redirect('customers')
        else:
            return render(request,'sales/customer_add.html',{'form_obj':form_obj,'cid':cid})

#添加或更改跟进记录
class ConsultRecord_add(View):
    def get(self,request,cid=None):
        obj_con = models.ConsultRecord.objects.filter(id=cid,).first()
        form_obj = myforms.ConsultRecordModelForm(request,instance=obj_con)
        return render(request,'sales/consultrecord_add.html',{'form_obj':form_obj,'cid':cid})

    def post(self,request,cid = None):
        next_url = request.GET.get('next')
        obj_list = models.ConsultRecord.objects.filter(id=cid).first()
        form_obj = myforms.ConsultRecordModelForm(request,request.POST,instance=obj_list)
        if form_obj.is_valid():
            form_obj.save()
            if cid:
                return redirect(next_url)
            else:
                return redirect('consultRecords')

        else:
            return render(request,'sales/consultrecord_add.html',{'form_obj':form_obj})

#跟进记录
class ConsultRecords(View):
    def get(self,request):
        path = request.path  #请求路径
        current_page_num = request.GET.get('page') #当前页面数
        get_data = request.GET.copy()
        action = request.GET.get('action')
        kw = request.GET.get('kw')
        cid = request.GET.get('cid')
        all_consultrecords = models.ConsultRecord.objects.filter(delete_status=False,
                             consultant__username = request.session.get('name'),).order_by('-id')
        if cid:
            all_consultrecords=all_consultrecords.filter(customer__id=cid)

        if kw and action:
            if action == 'status__contains':
                for i in models.seek_status_choices:
                    if kw in i:
                        kw = i[0]

            q = Q()
            q.children.append([action, kw])
            all_consultrecords = all_consultrecords.filter(q)
        all_num_count = all_consultrecords.count() #所有数据量
        page_obj = pager.Pagination(current_page_num,all_num_count,get_data,settings.PAGE_NUM_SHOW,
                                    settings.DATA_SHOW_NUMBER)
        page_html = page_obj.html()
        all_consultrecords = all_consultrecords[page_obj.start_data_num:page_obj.end_data_num]
        return render(request,'sales/consultrecord_list.html',{'all_consultrecords':all_consultrecords,'page_html':page_html})

    def post(self,request):
        bulk_aciton = request.POST.get('bilk_action') #批量操作
        cids = request.POST.getlist('cids')
        if hasattr(self,bulk_aciton):
            ret = getattr(self,bulk_aciton)(request,cids)
            if ret:
                return ret
            else:
                return redirect('consultRecords')
        else:
            return HttpResponse('你的操作有误')

    def bulk_delete(self,request,cids):
        models.ConsultRecord.objects.filter(id__in = cids).update(
            delete_status = True
        )
        return redirect('consultRecords')

#报名记录
class Enrollments(View):

    def get(self, request):
        path = request.path  # 请求路径
        current_page_num = request.GET.get('page')  # 当前页面数
        get_data = request.GET.copy()
        action = request.GET.get('action')
        kw = request.GET.get('kw')
        all_enrollments = models.Enrollment.objects.filter(delete_status=False,).order_by('-id')
        if kw and action:
            if action=="contract_approved":
                if kw in "是可以":
                    kw=True
                else:
                    kw=False
            q = Q()
            q.children.append([action, kw])
            all_enrollments = all_enrollments.filter(q)
        all_num_count = all_enrollments.count()  # 所有数据量
        page_obj = pager.Pagination(current_page_num, all_num_count, get_data, settings.PAGE_NUM_SHOW,
                                    settings.DATA_SHOW_NUMBER)
        page_html = page_obj.html()
        all_enrollments = all_enrollments[page_obj.start_data_num:page_obj.end_data_num]
        return render(request, 'sales/enrollments_list.html',
                      {'all_enrollments': all_enrollments, 'page_html': page_html})

    def post(self,request):
        bulk_aciton = request.POST.get('bilk_action') #批量操作
        eids = request.POST.getlist('eids')
        if hasattr(self,bulk_aciton):
            ret = getattr(self,bulk_aciton)(request,eids)
            if ret:
                return ret
            else:
                return redirect('enrollments')
        else:
            return HttpResponse('你的操作有误')

    def bulk_delete(self,request,eids):
        models.Enrollment.objects.filter(id__in = eids).update(
            delete_status = True
        )
        return redirect('enrollments')

#添加或更改报名记录
class Enrollments_add(View):

    def get(self,request,eid=None):
        obj_enr = models.Enrollment.objects.filter(id=eid).first()
        form_obj = myforms.EnrollmentModelForm(instance=obj_enr)
        return render(request, 'sales/enrollment_add.html', {'form_obj':form_obj,'eid':eid})

    def post(self,request,eid=None):
        next_url = request.GET.get('next')
        obj_list = models.Enrollment.objects.filter(id=eid).first()
        form_obj = myforms.EnrollmentModelForm(request.POST, instance=obj_list)
        if form_obj.is_valid():
            form_obj.save()
            if eid:
                return redirect(next_url)
            else:
                return redirect('enrollments')
        else:
            return render(request, 'sales/enrollment_add.html', {'form_obj': form_obj,'eid':eid})

#添加或更改报名记录
class Courserecords_add(View):

    def get(self,request,cid=None):

        obj_cr = models.CourseRecord.objects.filter(id=cid).first()
        form_obj = myforms.CourseRecordModelForm(instance=obj_cr,)
        return render(request,'sales/courserecord_add.html',{'form_obj':form_obj,'cid':cid})

    def post(self,request,cid=None):
        next_url = request.GET.get('next')
        obj_list = models.CourseRecord.objects.filter(id=cid).first()
        form_obj = myforms.CourseRecordModelForm(request.POST,instance=obj_list)
        if form_obj.is_valid():
            form_obj.save()
            if next_url:
                return redirect(next_url)
            else:
                return redirect('courserecords')
        else:
            return render(request, 'sales/courserecord_add.html', {'form_obj': form_obj, 'cid': cid})


#课程记录展示
class CourserecordsView(View):
    def get(self,request):
        cho = 1
        current_page_num = request.GET.get('page')
        get_data = request.GET.copy()
        action = request.GET.get('action')
        kw = request.GET.get('kw')
        courserecord_list = models.CourseRecord.objects.all().order_by('-id')
        if action and kw:
            q = Q()
            q.children.append([action,kw])
            courserecord_list = courserecord_list.filter(q)
        all_num_count = courserecord_list.count()
        page_obj = pager.Pagination(current_page_num, all_num_count, get_data, settings.PAGE_NUM_SHOW,
                                    settings.DATA_SHOW_NUMBER)
        page_html = page_obj.html()
        courserecord_list = courserecord_list[page_obj.start_data_num:page_obj.end_data_num]
        return render(request,'sales/courserecord_list.html',{'courserecord_list':courserecord_list,
                                                              'page_html': page_html,'cho':cho})

    def post(self,request):
        cids = json.loads(request.POST.get('cids_list'))
        action = request.POST.get('bulk_action')
        if hasattr(self,action):
            ret = getattr(self,action)(request,cids)
            return ret
        else:
            return HttpResponse('您的操作有误')

    def bulk_create_sr(self,request,cids):
        """
        批量生成学习记录
        :param request: 请求
        :param cids: 课程记录id
        :return:
        """
        ret = {'status':None}
        try:
            with transaction.atomic():
                for cid in cids:
                    course_obj = models.CourseRecord.objects.filter(id=cid).first()
                    students_objs = course_obj.re_class.customer_set.filter(status='studying')
                    for student in students_objs:
                        models.StudyRecord.objects.create(
                            course_record_id=cid,
                            student=student
                        )
            ret['status'] = 1
        except:
            ret['status'] = 0
        return JsonResponse(ret)

#学习记录
class StudyRecordView(View):
    def get(self,request):
        management = 1
        cid = request.GET.get('cid')
        current_page_num = request.GET.get('page')
        get_data = request.GET.copy()
        # action = request.GET.get('action')
        # kw = request.GET.get('kw')

        form_set = modelformset_factory(models.StudyRecord, myforms.StudyRecordModelForm, extra=0)
        if cid:
            study_obj = models.StudyRecord.objects.filter(course_record_id=cid)
            form_set = form_set(queryset=study_obj)
            all_num_count = study_obj.count()
            page_obj = pager.Pagination(current_page_num, all_num_count, get_data, settings.PAGE_NUM_SHOW,
                                        settings.DATA_SHOW_NUMBER)
            all_studyrecords = study_obj[page_obj.start_data_num:page_obj.end_data_num]
        else:
            study_obj_plus = models.StudyRecord.objects.all()
            all_num_count = study_obj_plus.count()
            page_obj = pager.Pagination(current_page_num, all_num_count, get_data, settings.PAGE_NUM_SHOW,
                                        settings.DATA_SHOW_NUMBER)

            all_studyrecords = study_obj_plus[page_obj.start_data_num:page_obj.end_data_num]
        page_html = page_obj.html()
        # if action and kw:
        #     q = Q()
        #     q.children.append([action,kw])
        #     form_set.queryset = q
        # all_num_count = form_set.queryset.count()

        return render(request,'sales/studyrecord_list.html',{'form_set':form_set,'management':management,
                    'all_studyrecords':all_studyrecords,'page_html':page_html})

    def post(self,request):
        management = 1
        form_set = modelformset_factory(models.StudyRecord,myforms.StudyRecordModelForm,extra=0)
        form_set = form_set(request.POST)
        if form_set.is_valid():
            form_set.save()
            return redirect(request.path)
        else:
            return render(request, 'sales/studyrecord_list.html', {'form_set': form_set,'management':management})


# def customer_del(request,cid):
#     ret_data = {'status':None,}
#     # print(66666666666666666666666666666666666666)
#     if request.method == "GET":
#         try:
#             # cid = request.POST.get('id')
#             # print(cid,555555555555)
#             models.Customer.objects.filter(id=cid).update(
#                 delete_status = True,
#             )
#             ret_data['status'] = 1
#         except Exception:
#             ret_data['status'] = 2
#         return JsonResponse(ret_data)
#     return redirect('customers')

#删除客户

#删除客户
def customer_del(request,cid):
    """
    删除客户
    :param request:
    :param cid: 客户的id
    :return:
    """
    models.Customer.objects.filter(id=cid).update(
        delete_status = True
    )
    return redirect('customers')

#删除跟进记录
def consultrecord_del(request,cid):
    """
    删除跟进记录
    :param request:
    :param cid: 跟进记录的id
    :return:
    """
    models.ConsultRecord.objects.filter(id=cid).update(
        delete_status = True
    )
    return redirect('consultRecords')

#删除报名记录
def enrollment_del(request,eid):
    """
    删除报名记录
    :param request:
    :param eid: 报名记录的id
    :return:
    """
    models.Enrollment.objects.filter(id=eid).update(
        delete_status = True
    )
    return redirect('enrollments')

#删除课程记录
def courserecord_del(request,cid):
    """
    删除课程记录
    :param request:
    :param cid: 课程记录的id
    :return:
    """
    models.CourseRecord.objects.filter(id=cid).delete()
    return redirect('courserecords')

#注销
def logout(request):
    """
    注销
    :param request:
    :return:
    """
    request.session.flush()
    print("已注销")
    return redirect('login')