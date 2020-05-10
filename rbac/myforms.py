from django import forms
from rbac import models
from rbac.serve.icons import icon_list

class RoleModelForm(forms.ModelForm):
    class Meta:
        model = models.Role
        fields = "__all__"
        exclude = ['permissions',]
        labels = {
            'name':'角色',
        }
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control'})
        }

class MenuModelForm(forms.ModelForm):
    class Meta:
        model = models.Menu
        fields = "__all__"

        widgets = {
            'title':forms.TextInput(attrs={'class':'form-control'}),
            'weight':forms.TextInput(attrs={'class':'form-control'}),
            'icon':forms.RadioSelect(choices=icon_list),
        }

class PermissionModelForm(forms.ModelForm):
    class Meta:
        model=models.Permission
        fields = "__all__"
        # widgets={
        #     # 'icon':forms.RadioSelect(choices=icon_list),
        # }

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {'class': 'form-control'}
            )


class MultiPermissionModelForm(forms.ModelForm):
    class Meta:
        model = models.Permission
        fields = ['title','url','url_name','parent','menu']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {'class':'form-control'}
            )
        self.fields['parent'].choices = [(None,'------')] + list(
            models.Permission.objects.filter(parent__isnull=True).exclude(
                menu__isnull=True
            ).values_list('id','title')
        )

    # def clean(self):
        # menu = self.cleaned_data.get('menu_id')
        # pid = self.cleaned_data.get('parent_id')
        # print(self.cleaned_data)
        # if menu and pid:
        #     raise forms.ValidationError('菜单和跟权限同时只能选择一个')
        # return self.changed_data