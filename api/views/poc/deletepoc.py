from django.http import JsonResponse
from django.views import View
from app.models import Poc_info
import os

# 项目删除视图
class deletepoc(View):
    def post(self, request):
        res = {
            'code': 500,
            'msg': "删除成功",
            'self': None,
        }

        data = request.data
        if not data.get('id'):
            res['self'] = 'scan'
            res['msg'] = '请选择对应资产'
            return JsonResponse(res)

        id_list = data.get('id')
        for id in id_list:
            poc_info = Poc_info.objects.filter(id=id).first()
            if poc_info:
                # 使用数据库中存储的文件路径
                file_path = poc_info.content
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                # 删除数据库记录
                poc_info.delete()
        res['code'] = 200
        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})