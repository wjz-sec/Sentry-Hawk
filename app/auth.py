from django.shortcuts import redirect
from django.http import JsonResponse
import time

def is_login_fun(fun):
    def inner(*args,**kwargs):
        request = args[0]
        if not request.user.is_authenticated:
            return redirect('/login/')
        res = fun(*args,**kwargs)
        return res
    return inner

#判断用户是否登录,类视图
def is_login_method(fun):
    def inner(*args,**kwargs):
        request = args[1]
        if not request.user.is_authenticated:
            return JsonResponse({'code':666,'msg':'请登录'})
        res = fun(*args,**kwargs)
        return res
    return inner