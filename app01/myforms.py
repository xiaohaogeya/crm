from django import forms
from django.core.exceptions import ValidationError
from app01 import models
import re
def moblie_validate(value):
    moblie_re =re.compile(r'.*--.*')
    if moblie_re.match(value):
        raise ValidationError('不能包含--特殊字符')

def phone_validate(value):
    phone_re = re.compile(r'^(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$')
    if not phone_re.match(value):
        raise ValidationError('手机格式错误')

class UserForm(forms.Form):
    username = forms.CharField(
        min_length=2,
        max_length=32,
        widget=forms.TextInput(attrs={'placeholder':"请输入您的用户名",'class':'username','autocomplete':'off'}),
        validators=[moblie_validate,],
        error_messages={
            'required':'用户名不能为空',
            'min_length':"用户名最短2位",

        }
    )
    password=forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={'class':'password','placeholder':'输入密码','oncontextmenu':'return false','onpaste':'return false',}),
        error_messages={
            'required':'密码不能为空',
            'min_length':'密码最短6位',
        }
    )
    password_again=forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={'class':'password','placeholder':'再次输入密码','oncontextmenu':'return false','onpaste':'return false',}),
        error_messages={
            'required':'密码不能为空',
            'min_length':'密码最短6位',
        }
    )
    telephone = forms.CharField(
        validators=[phone_validate,],
        widget=forms.TextInput(attrs={'placeholder': "请输入您的电话号码"}),
        error_messages={
            'required':'电话号码不能空',
        }
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': "请输入您的163邮箱"}),
        error_messages={
            'required': '邮箱不能空',
        }
    )

    def clean_username(self):
        value = self.cleaned_data.get('username')
        ret = models.UserInfo.objects.filter(
            username=value,
        )
        if ret:
            raise ValidationError('用户名已存在')
        else:
            return value

    def clean_telephone(self):
        value = self.cleaned_data.get('telephone')
        if len(value) != 11:
            raise ValidationError('手机好长度不对')
        else:
            return value

    def clean_email(self):
        value = self.cleaned_data.get('email')
        ret = re.compile(r'\w+@163.com$')
        if ret.match(value):
            return value
        else:
            raise ValidationError('必须是163邮箱')

    def clean(self):
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('password_again')
        if p1 == p2:
            return self.cleaned_data
        else:
            self.add_error('password_again','两次密码不一致')


    # def __init__(self,*args,**kwargs):
    #     super().__init__(*args,**kwargs)
    #     for name,field in self.fields.items():
    #         field.widget.attrs.update({'class':'form-control'})
    # def clean_username(self):

class CustomerModelForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields='__all__'
        exclude = ['delete_status',]
        widgets = {
            'birthday':forms.TextInput(attrs={'type':'date'}),
            'next_date':forms.TextInput(attrs={'type':'date'}),
        }

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for name,filed in self.fields.items():
            # print(name)
            if name != "course":
                filed.widget.attrs.update({'class':'form-control'})


class ConsultRecordModelForm(forms.ModelForm):
    class Meta:
        model = models.ConsultRecord
        fields = "__all__"
        exclude=['delete_status']

    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for name,field in self.fields.items():
            if name == "customer":
                field.queryset = models.Customer.objects.filter(consultant__username = request.session.get('name'))
            elif name == "consultant":
                userinfo_obj = models.UserInfo.objects.filter(username=request.session.get('name'))
                field.choices = [(i.id,i.username) for i in userinfo_obj]
            field.widget.attrs.update({'class':'form-control'})


class EnrollmentModelForm(forms.ModelForm):
    class Meta:
        model=models.Enrollment
        fields="__all__"
        exclude=['delete_status',]

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for name,filed in self.fields.items():
            if name == 'customer':
                filed.queryset = models.Customer.objects.filter(delete_status=False)
            filed.widget.attrs.update({'class':'form-control'})


class CourseRecordModelForm(forms.ModelForm):
    class Meta:
        model=models.CourseRecord
        fields="__all__"

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for name,filed in self.fields.items():
            filed.widget.attrs.update({'class':'form-control'})


class StudyRecordModelForm(forms.ModelForm):
    class Meta:
        model=models.StudyRecord
        fields="__all__"