

print(divmod(20,10))



import os

if __name__ == '__main__':

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings")
    import django
    django.setup()

    import random
    from app01 import models

    c_list = []

    for i in range(521):

        obj = models.Customer(
            qq=f'{i+1}{i+2}{i+3}',
            name='小骚浩%s'%i,
            course=['PythonFullStack',],

        )
        c_list.append(obj)
    models.Customer.objects.bulk_create(c_list)













