from django import template
from django.urls import reverse
from django.http.request import QueryDict
from app01 import models
register = template.Library()

@register.filter
def list_number(request,forloop_counter):
    current_page = request.GET.get('page')
    try:
        current_page = int(current_page)
    except:
        current_page = 1
    return (current_page -1)*10 + forloop_counter

@register.simple_tag
def resolve_url(request,url_name,cid):
    """

    :param request: 请求对象
    :param url_name: url别名
    :param cid: 客户id
    :return:
    """
    custom_qd = QueryDict(mutable=True)
    custom_qd['next'] = request.get_full_path()
    next_url = custom_qd.urlencode()
    reverse_url = reverse(url_name,args=(cid,))
    full_path = reverse_url + '?' + next_url
    return full_path




@register.filter
def repalce_info(info):
    if info:
        return "是"
    else:
        return "否"


@register.filter
def tihuan(info):
    for i in models.course_choices:
        if info in i:
            info = i[1]
    return info