from django.views import View
from django.http import JsonResponse
from django import forms
from app.models import UserInfo
from django.contrib import auth
import re

class signForms(forms.Form):
    name = forms.CharField(error_messages={'required': '请输入用户名'})
    phone_num = forms.CharField(error_messages={'required': '请输入手机号'})
    mail = forms.CharField(error_messages={'required': '请输入邮箱'})
    pwd = forms.CharField(widget=forms.PasswordInput, error_messages={
        'required': '请输入密码',
        'min_length': '密码长度必须至少为8位'
    })
    repwd = forms.CharField(error_messages={'required': '请输入确认密码'})

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        user = UserInfo.objects.filter(username=name).first()
        if user:
            self.add_error('name', '当前用户已存在')
        return name

    def clean_phone_num(self):
        phone_num = self.cleaned_data.get('phone_num')
        user = UserInfo.objects.filter(phone_num=phone_num).first()
        if not re.match(r'^1[3-9]\d{9}$', phone_num):
            self.add_error('phone_num', '请输入有效的手机号码')
        if user:
            self.add_error('phone_num', '手机号码已存在')
        return phone_num

    def clean_mail(self):
        mail = self.cleaned_data.get('mail')
        user = UserInfo.objects.filter(mail=mail).first()
        if not forms.EmailField().clean(mail):
            self.add_error('mail', '请输入有效的邮箱地址')
        if user:
            self.add_error('mail', '邮箱已存在')
        return mail

    def clean_pwd(self):
        pwd = self.cleaned_data.get('pwd')
        if len(pwd) < 8:
            self.add_error('pwd', '密码长度必须至少为8位')
        return pwd

    def clean(self):
        pwd = self.cleaned_data.get('pwd')
        re_pwd = self.cleaned_data.get('repwd')
        if pwd != re_pwd:
            self.add_error('repwd', '两次密码不一致')
        return self.cleaned_data


def clean_form(form):
    err_dict: dict = form.errors
    err_valid = list(err_dict.keys())[0]
    err_msg = err_dict[err_valid][0]
    return err_valid, err_msg

class signViews(View):
    def post(self, request):
        res = {
            'code': 425,
            'msg': "注册成功！",
            "self": None
        }
        form = signForms(request.data, request=request)

        if not form.is_valid():
            # 验证不通过
            res['self'], res['msg'] = clean_form(form)
            return JsonResponse(res)

        user = UserInfo.objects.create_user(
            username=request.data.get('name'),
            password=request.data.get('pwd'),
            nick_name=request.data.get('name'),
            phone_num=request.data.get('phone_num'),
            mail=request.data.get('mail'),
        )
        # 注册之后直接登录
        auth.login(request, user)
        res['code'] = 0

        return JsonResponse(res)


