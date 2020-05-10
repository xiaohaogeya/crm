from django.contrib import admin
from rbac import models
# Register your models here.


class PermissionAdmin(admin.ModelAdmin):
    list_display = ['id','url','title','menu','icon','parent_id','url_name']
    list_editable = ['url','title','menu','icon','url_name']


admin.site.register(models.Menu)

admin.site.register(models.Role)
admin.site.register(models.Permission,PermissionAdmin)