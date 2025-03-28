from django.http import JsonResponse
from django.views import View
import json
class getAuthButtonList(View):
    def get(self,request):
        user = 'admin'  # 临时硬编码为'admin'，实际应用中应该从请求中获取

        if user == 'admin':
            file_path = 'api/menu_static/authButtonList.json'  # 使用完整的文件路径
        else:
            res = {
                'code': 500,
                'msg': '获取权限失败',
                'data': {},
            }
            return JsonResponse(res)

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                menu_data = json.load(file)
                return JsonResponse(menu_data)  # 返回JsonResponse对象
        except FileNotFoundError:
            # 如果文件不存在，返回错误信息
            res = {
                'code': 500,
                'msg': '菜单文件未找到',
                'data': {},
            }
            return JsonResponse(res)
        except json.JSONDecodeError:
            # 如果JSON格式不正确，返回错误信息
            res = {
                'code': 500,
                'msg': '菜单文件格式错误',
                'data': {},
            }
            return JsonResponse(res)
