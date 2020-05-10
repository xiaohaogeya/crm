from django.conf import settings
from django.utils.module_loading import import_string
from django.urls import RegexURLPattern,RegexURLResolver
from collections import OrderedDict

def recursion_urls(pre_namespace,per_url,urlpatterns,url_ordered_dict):

    for item in urlpatterns:
        if isinstance(item,RegexURLResolver):
            if pre_namespace:
                if item.namespace:
                    namespace = "%s:%s"%(pre_namespace,item.namespace)
                else:
                    namespace = pre_namespace
            else:
                if item.namespace:
                    namespace = item.namespace
                else:
                    namespace = None
            recursion_urls(namespace,per_url + item.regex.pattern,item.url_patterns,url_ordered_dict)
        else:
            if pre_namespace:
                name = "%s:%s"%(pre_namespace,item.name)
            else:
                name = item.name
            if not item.name:
                raise Exception('URL路由必须设置name属性')

            url = per_url + item._regex
            url_ordered_dict[name] = {'url_name':name,'url':url.replace('^','').replace('$','')}

#获取路由
def get_all_url_dict(ignore_namespace_list=None):
    ignore_list = ignore_namespace_list or []
    #有序字典
    url_ordered_dict = OrderedDict()
    #获取项目的URL
    md = import_string(settings.ROOT_URLCONF)
    # print(md,666666666666)
    urlpatterns = []
    for item in md.urlpatterns:
        if isinstance(item,RegexURLResolver) and item.namespace in ignore_list:
            continue
        urlpatterns.append(item)

    recursion_urls(None,'/',urlpatterns,url_ordered_dict)
    return url_ordered_dict