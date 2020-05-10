import re

from django.shortcuts import render,redirect,HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse


class Auth(MiddlewareMixin):
    white_list = [reverse('login'),reverse('register'),'/admin.*']
    def process_request(self,request):

        current_path = request.path #当前请求路径
        for re_path in self.white_list:
            reg = r'^%s$'%re_path
            if re.search(reg,current_path):
                break
        else:
            username = request.session.get('name')
            if not username:
                return redirect('login')



        # if request.path in self.white_list:
        #     pass
        # else:
        #     is_login = request.session.get('is_login')
        #     if is_login== True:
        #         pass
        #     else:
        #         return redirect('login')