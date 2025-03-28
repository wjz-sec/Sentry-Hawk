from django.http import JsonResponse
from django.views import View


# 获取所有资产类型(固定值!!!新增要改)
class getAssetType(View):
    def get(self, request):
        res = {
            'code': 200,
            'data': [{"type": "URL"}, {"type": "Domain"}, {"type": "IP"}],
        }
        return JsonResponse(res, safe=False, json_dumps_params={'ensure_ascii': False})
# 获取所有的客户单位