from django.db import models

# Create your models here.

class Menu(models.Model):
    """
    一级菜单表
    """
    title = models.CharField(max_length=32,verbose_name='菜单名称')
    weight = models.IntegerField(default=100, verbose_name='权重')
    icon = models.CharField(max_length=32,null=True,blank=True,verbose_name='图标')


    def __str__(self):
        return self.title


class Role(models.Model):
    name = models.CharField(max_length=16)
    permissions = models.ManyToManyField('Permission')

    def __str__(self):
        return self.name

class Userinfo(models.Model):

    roles = models.ManyToManyField(Role)

    class Meta:
        abstract = True #本类不去生成数据库的表



class Permission(models.Model):
    url = models.CharField(max_length=1000,verbose_name='路由地址')
    title = models.CharField(max_length=32,verbose_name='路由名称') #客户展示
    # is_menu = models.BooleanField(default=False) #通过这个字段判断这条权限是否是左侧菜单权限
    icon = models.CharField(max_length=32,null=True,blank=True,verbose_name='菜单图标') #菜单图标
    menu = models.ForeignKey('Menu',null=True,blank=True,verbose_name='一级菜单')
    parent = models.ForeignKey('self',null=True,blank=True,verbose_name='二级菜单及权限')
    url_name = models.CharField(max_length=32,null=True,blank=True,verbose_name='路由别名')


    def __str__(self):
        return self.title