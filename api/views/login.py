from django.views import View
from django.http import JsonResponse
from django import forms
from app.models import UserInfo
from django.contrib import auth
from app.auth import is_login_method
from rest_framework.authtoken.models import Token
import random


class LoginForms(forms.Form):
    username = forms.CharField(error_messages={'required': '请输入用户名'})
    password = forms.CharField(error_messages={'required': '请输入密码'})
    # code = forms.CharField(error_messages={'required': '请输入验证码'})

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        user = UserInfo.objects.filter(username=username).first()
        if not user:
            self.add_error('username', '当前用户不存在')
        return username

    def clean_code(self):
        request = self.request
        code: str = self.cleaned_data.get('code')
        valid_code: str = request.session.get('valid_code')
        if valid_code.upper() != code.upper():
            self.add_error('code', '验证码错误')
        return code

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = auth.authenticate(username=username,password=password)
        if not user:
            self.add_error('username', '用户名或密码错误')
        self.cleaned_data['user'] = user
        return self.cleaned_data


def clean_form(form):
    err_dict: dict = form.errors
    err_valid = list(err_dict.keys())[0]
    err_msg = err_dict[err_valid][0]
    return err_valid,err_msg

class LoginViews(View):
    def post(self, request):
        res = {
            'code': 500,
            'msg': '登录成功',
            'self': None,
            'data': {'access_token': None},
        }
        data = request.data
        form = LoginForms(data, request=request)
        if not form.is_valid():
            res['self'],res['msg'] = clean_form(form)
            return JsonResponse(res)

        user = form.cleaned_data['user']
        auth.login(request, user)

        # 获取或创建用户的 token
        # token, created = Token.objects.get_or_create(user=user)
        # res['access_token'] = token.key  # 将 token 的 key 添加到响应中
        res['data']['access_token'] = 'bqddxxwqmfncffacvbpkuxvwvqrhln'
        res['data']['userInfo'] = {"name": form.cleaned_data['username']}
        res['code'] = 200
        return JsonResponse(res)

class EditPasswordForms(forms.Form):
    old_pwd = forms.CharField(error_messages={'required': '请输入原密码'})
    password = forms.CharField(error_messages={'required': '请输入新密码'})
    re_password = forms.CharField(error_messages={'required': '请再次输入新密码'})

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def clean_old_pwd(self):
        user = self.request.user
        old_pwd = self.cleaned_data['old_pwd']

        user = auth.authenticate(username=user.username,password=old_pwd)
        if not user:
            return self.add_error('old_pwd','原密码错误')
        self.cleaned_data['user'] = user
        return old_pwd


class EditPasswordView(View):
    @is_login_method
    def post(self, request):
        res = {
            'code': 344,
            'msg' : '密码修改成功，请重新登录！',
            'self' : None
        }
        data = request.data
        form = EditPasswordForms(data,request=request)
        if not form.is_valid():
            res['self'],res['msg'] = clean_form(form)
            return JsonResponse(res)

        user = form.cleaned_data['user']
        user.set_password(form.cleaned_data['password'])
        user.save()
        auth.logout(request)
        res['code'] = 0
        return JsonResponse(res)


class LogoutViews(View):
    def post(self, request):
        res = {
            'code': 200,
            'msg': '退出成功'
        }
        auth.logout(request)
        return JsonResponse(res)